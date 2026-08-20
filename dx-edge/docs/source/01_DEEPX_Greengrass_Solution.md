# DEEPX Greengrass Solution

**Simplifying Edge AI Deployment — Over-the-Air Deployment with the DEEPX DX-M1 NPU and AWS IoT**

Edge AI delivers value only when models run reliably in the field. It is not enough to run a model once. You must be able to deploy the same runtime environment to different pieces of equipment and manage operational status and versions consistently across all of them.

Running a model on a single camera and a single edge AI device is relatively simple. The picture changes as devices multiply across stores, factories, and logistics sites. You have to install an NPU driver that matches each device's operating system and kernel, align firmware and runtime versions, and convert models trained in the cloud into a format the NPU can execute. Repeating this process at every site lengthens deployment time and increases the chance of version mismatches.

This document describes how to simplify that process by combining DEEPX DX-M1 series NPUs with AWS IoT services. You first prepare the DEEPX compilation environment and the required AWS resources through AWS Marketplace, then convert an ONNX model into the DXNN format used by DEEPX NPUs. You then connect devices to the cloud with AWS IoT Core and use AWS IoT Greengrass as the edge platform to deploy the NPU driver, firmware, the dx_rt runtime, and the dx_stream media pipeline to a device group over the air.

> **Note — Key takeaway**
>
> DEEPX handles low-power on-device inference, while AWS IoT Core and AWS IoT Greengrass manage device connectivity, group-level deployment, component lifecycle, and update status. Combining the two products connects the process of preparing a model for the NPU and the process of deploying an identical runtime environment to many edge devices into a single flow.

This document proceeds in the following order.

1. DEEPX NPU and the edge AI deployment challenge
2. End-to-end architecture combining DEEPX and AWS IoT
3. Preparing the compilation environment with AWS Marketplace
4. Runtime OTA deployment through AWS IoT Core and Greengrass
5. Verifying deployment and inference on the edge device

---

## 1. DEEPX NPU and the Edge AI Deployment Challenge

DEEPX develops NPUs that perform deep learning inference in edge environments where power and space are limited. The DX-M1 series used in this document is an AI accelerator that connects to a host in the M.2 form factor. The DEEPX DX-M1 can be paired with an Arm-based device such as a Raspberry Pi 5 or with an x86-based industrial PC to run vision models such as object detection, face recognition, and OCR in the field. Running inference where the video is produced means you do not have to send raw video to the cloud at all times, which helps reduce latency and network usage.

![Figure 1. The DEEPX NPU product family](img/greengrass/fig01_npu_lineup.png)

*Figure 1. The DEEPX NPU product family. This document focuses on the DX-M1 series of edge NPUs.*

NPU performance alone is not enough for field operations. As the number of devices grows, you need to manage the versions and deployment status of drivers, firmware, runtimes, and models remotely, and to redeploy models improved on the basis of operational data.

Along with the chip, DEEPX provides a compiler that converts ONNX models into DXNN, the NPU execution format. After subscribing to DEEPX Greengrass Solution in AWS Marketplace and setting up the required environment, you upload an ONNX model and a compilation configuration JSON file to Amazon S3. An event-driven compilation workflow then converts the model to DXNN and stores the result under the same S3 path.

AWS IoT Core and AWS IoT Greengrass connect this compilation flow to field operations. AWS IoT Core manages edge devices and thing groups, and AWS IoT Greengrass deploys the edge runtime to target devices. The resulting DXNN model can be used by an inference application, and the way model artifacts are delivered to devices can be aligned with the deployment design of the application or of a Greengrass component.

---

## 2. End-to-End Architecture Combining DEEPX and AWS IoT

Solving these operational challenges requires connecting the process of preparing a model in a format the NPU can run with the process of deploying the resulting runtime environment consistently across many devices. The DEEPX Compiler, AWS IoT Core, and AWS IoT Greengrass each play a different role in this flow.

![Figure 2. End-to-end flow of the DEEPX Greengrass Solution](img/greengrass/fig02_solution_overview.png)

*Figure 2. End-to-end flow of the DEEPX Greengrass Solution, connecting model preparation with edge deployment*

| Feature | Description |
| :--- | :--- |
| **Single-stack deployment** | A single AWS CloudFormation stack provisions both the cloud model compilation infrastructure and the edge runtime deployment environment. |
| **Event-driven compilation pipeline** | A workflow built on Amazon S3, AWS Lambda, and AWS Step Functions converts ONNX models into the DXNN format used by DEEPX NPUs. The EC2 instance used for compilation runs only while a job is active and is terminated when the job finishes. |
| **Automated runtime deployment (ZTP)** | AWS IoT Greengrass installs the NPU driver, firmware, dx_rt, and dx_stream over the air. Both the classic Greengrass nucleus and Greengrass nucleus lite for constrained devices are supported. |

The end-to-end flow has two main parts. The first is model preparation, in which an ONNX model is converted in the cloud into a DXNN artifact that a DEEPX NPU can run. The second is edge deployment, in which devices connected to AWS IoT Core are grouped into a thing group and DEEPX runtime components are delivered to those devices through a Greengrass deployment.

![Figure 3. Cloud compilation pipeline and runtime deployment architecture](img/greengrass/fig03_architecture.png)

*Figure 3. Cloud compilation pipeline and AWS IoT Greengrass runtime deployment architecture*

In the cloud, uploading an ONNX model and a compilation configuration JSON file to Amazon S3 starts an event-driven workflow. AWS Lambda and AWS Step Functions launch a temporary EC2 instance based on the DEEPX Compiler AMI and invoke the `dxcom` compiler through AWS Systems Manager Run Command. When compilation finishes, the DXNN artifact is stored in S3 and the EC2 instance is terminated. Execution status and detailed logs are available in AWS Step Functions and Amazon CloudWatch Logs.

At the edge, AWS IoT Core manages devices and thing groups, and AWS IoT Greengrass deploys the DEEPX runtime at the group level. Devices install the NPU driver, firmware, dx_rt, and dx_stream through an AWS IoT Greengrass component and report deployment status back to the cloud. This lets you apply the same runtime environment consistently across many edge devices without connecting to each one directly.

### Zero-Touch Provisioning

To simplify field deployment and operations, the DEEPX Greengrass Solution provides Zero-Touch Provisioning (ZTP). When you add a registered device to the thing group, Greengrass delivers the `com.deepx.dx-runtime` component, which automatically installs the driver, firmware, dx_rt, and dx_stream and reports the result to the cloud. Operators can manage new equipment and runtime updates consistently at the group level without connecting to each device over SSH.

> **Note — Scope of ZTP**
>
> In this document, ZTP covers the automatic deployment of the runtime environment to devices already registered with AWS IoT Core. Automating certificate injection during manufacturing or fleet provisioning at first boot requires a separate device provisioning design.

---

## 3. Preparing the Compilation Environment with AWS Marketplace

The previous section described the cloud compilation path that converts an ONNX model to DXNN and the flow that deploys the runtime to edge devices through Greengrass. This section walks through setting up and running the model preparation path. You subscribe to the DEEPX solution in AWS Marketplace, deploy the CloudFormation stack, and then upload a sample ONNX model to S3 to review the DXNN output and the compilation logs.

### Prerequisites

Prepare the following before you begin.

- An AWS account and permissions to create a CloudFormation stack
- An edge device with a DEEPX DX-M1 M.2 module installed. For example, you can use an arm64 host such as a Raspberry Pi 5 or an x86_64 Ubuntu host.
- A device with AWS IoT Greengrass Core V2 installed and registered with AWS IoT Core. If the device is a target for runtime OTA deployment, it must belong to the thing group.
- The ONNX model to compile and its JSON configuration file
- An existing VPC and subnet in which to run the compiler EC2 instance. The subnet must be able to reach the required AWS services, including Amazon S3, AWS Systems Manager, and Amazon CloudWatch Logs, over HTTPS. If you use a private subnet, configure a NAT gateway or the necessary VPC endpoints.

### Subscribing in Marketplace and Preparing the Environment

Subscribe to [DEEPX Greengrass Solution](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34) in AWS Marketplace. AWS resource charges apply separately; see the AWS Marketplace listing for current software pricing and subscription terms. If you want the model compilation capability without edge device runtime deployment, you can subscribe to [DEEPX Compiler Solution](02_DEEPX_Compiler_Solution.md) instead.

![Figure 4. Subscription page for the DEEPX solution in AWS Marketplace](img/greengrass/fig04_marketplace_listing.png)

*Figure 4. Subscription page for the DEEPX solution in AWS Marketplace*

**Step 1.** In AWS Marketplace, search for DEEPX Greengrass Solution, select it, and subscribe.

**Step 2.** Choose the AWS Region to deploy in and choose **Launch with CloudFormation**.

**Step 3.** Enter the values required to create the stack.

| Parameter | Description |
| :--- | :--- |
| `ImageId` | The SSM parameter path that points to the DX Compiler AMI. It resolves automatically to the AMI ID for the Region, so keep the default value. |
| `ModelBucketName` | The name of the S3 bucket that stores the ONNX input files and the DXNN compilation results. The name must be globally unique. |
| `InstanceType` | The EC2 instance type used for compilation. The default is `t3.xlarge`. |
| `VpcId` / `SubnetId` | The existing VPC and subnet in which the compiler instance runs. They must allow outbound HTTPS access to AWS services such as Amazon S3, AWS Systems Manager, and Amazon CloudWatch Logs. |
| `ThingGroupName` | The name of the IoT thing group targeted by the runtime deployment. If you leave it blank, a `<stack-name>-cores` group is created; if you enter the name of an existing group, that group is used. |

**Step 4.** Choose **Next** to go to the review page, then choose **Submit**.

When stack creation completes, note `ModelBucketName`, `StateMachineArn`, and `CompilerExecutionLogGroupName` in the CloudFormation **Outputs**. The rest of this procedure uses these values to upload models and check workflow status and compilation logs.

### Uploading an ONNX Model and Compiling Automatically

Prepare the model and configuration file to compile. In addition to models you train yourself, you can download pre-trained models validated for DEEPX NPUs from the [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/) and compile them directly. This example uses the `yolov5-s-face_640x640.onnx` model together with a JSON configuration file of the same name. Both files must be uploaded to the same S3 path, and you should use a dedicated prefix per model so that configuration files for different models do not get mixed together.

The configuration file defines the input tensor shape and the calibration method. You can specify a local path in `dataset_path`, but at compilation time this solution automatically replaces that value with `/opt/dx-compiler/calibration_dataset`, the calibration dataset path included in the AMI.

```json
{
  "inputs": {
    "input.1": [1, 3, 640, 640]
  },
  "calibration_num": 100,
  "calibration_method": "ema",
  "default_loader": {
    "dataset_path": "/mnt/datasets/widerface/WIDER_val/images",
    "file_extensions": ["jpeg", "jpg", "png"]
  }
}
```

Now upload the ONNX model and the JSON configuration file to the same S3 prefix to start compilation. The following commands retrieve the model bucket name from the CloudFormation outputs, download the sample model from the DEEPX Model Zoo, and upload both files to a dedicated per-model path.

```bash
export STACK_NAME=<cloudformation-stack-name>

export MODEL_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='ModelBucketName'].OutputValue" \
  --output text)

export MODEL_PREFIX=models/yolov5-s-face_640x640

# Download the ONNX model
curl -fLO https://sdk.deepx.ai/modelzoo/onnx/yolov5-s-face_640x640.onnx

# Save the configuration example above as a JSON file with the same name
cat > yolov5-s-face_640x640.json <<'EOF'
{
  "inputs": {
    "input.1": [1, 3, 640, 640]
  },
  "calibration_num": 100,
  "calibration_method": "ema",
  "default_loader": {
    "dataset_path": "/mnt/datasets/widerface/WIDER_val/images",
    "file_extensions": ["jpeg", "jpg", "png"]
  }
}
EOF

aws s3 cp --only-show-errors yolov5-s-face_640x640.onnx "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"
aws s3 cp --only-show-errors yolov5-s-face_640x640.json "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"
```

![Figure 5. Uploading the ONNX model and the compilation configuration file to the same S3 path](img/greengrass/fig05_s3_upload.png)

*Figure 5. Uploading the ONNX model and the compilation configuration file to the same Amazon S3 path*

When both files are uploaded, an Amazon S3 event starts the workflow. You can track workflow progress in the AWS Step Functions console. The workflow starts the instance, runs the compilation, polls for status, and then terminates the instance. It is designed to terminate the instance on failure paths as well.

![Figure 6. Step Functions compilation workflow execution result](img/greengrass/fig06_stepfunctions_succeeded.png)

*Figure 6. AWS Step Functions compilation workflow execution result (Succeeded)*

Use the following commands to check the status of recent executions.

```bash
export STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='StateMachineArn'].OutputValue" \
  --output text)

aws stepfunctions list-executions \
  --state-machine-arn "$STATE_MACHINE_ARN" \
  --max-results 5 \
  --query "executions[].[status,startDate,stopDate,name]" \
  --output table
```

After the workflow completes, look for the compiled `.dxnn` file in the same S3 directory as the source model. Detailed compilation logs are written to the `/dx-compiler/<stack-name>/execution` log group in Amazon CloudWatch Logs.

```bash
export COMPILER_LOG_GROUP=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='CompilerExecutionLogGroupName'].OutputValue" \
  --output text)

aws logs tail "$COMPILER_LOG_GROUP" --since 1h --follow
```

In the logs, you should see messages for the S3 download of the model and JSON file, the `dxcom` run, and the `.dxnn` upload, in that order.

```bash
aws s3 ls "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"
# yolov5-s-face_640x640.onnx
# yolov5-s-face_640x640.json
# yolov5-s-face_640x640.dxnn
```

Because this approach starts an EC2 instance only when there is a compilation job and terminates it afterward, you do not need to run a compilation server continuously.

---

## 4. Deploying the DEEPX Runtime to the Edge with AWS IoT Greengrass

In this step, you deploy the DEEPX runtime to Greengrass core devices that are registered with AWS IoT Core and belong to the target thing group. AWS IoT Core manages devices, certificates, and thing groups, and AWS IoT Greengrass deploys components and configuration to that group over the air. As a result, operators can apply the same runtime environment at the group level and check its status without connecting to each device over SSH.

> **Note — The `com.deepx.dx-runtime` component**
>
> This is the Greengrass component published by the CloudFormation stack. It installs the NPU driver, firmware, dx_rt, and dx_stream on the target device to prepare a DEEPX runtime environment for running DXNN models, and it reports the installation result to Greengrass.

The `com.deepx.dx-runtime` component published by the CloudFormation stack installs the following software in order.

- **NPU Linux driver**: Uses DKMS to build the driver for the target device's kernel
- **Firmware**: Updates the DX-M1 NPU firmware using `dxcli`
- **dx_rt**: The DEEPX C/C++ runtime for NPU detection and model execution
- **dx_stream**: A video inference pipeline that integrates OpenCV and GStreamer

The stack deploys this component to the target thing group. If you specified `ThingGroupName`, that group is used; if you left it blank, a `<stack-name>-cores` group is created. If the group contains core devices, the Greengrass deployment starts automatically.

![Figure 7. Checking AWS IoT Greengrass deployment status](img/greengrass/fig07_greengrass_deployment.png)

*Figure 7. Checking whether the target devices succeeded in the AWS IoT Greengrass deployment status*

In the Greengrass console, confirm that the deployment status is **Completed**. For any device that reports a problem, use the component logs to diagnose it. The commands for checking logs on the classic Greengrass nucleus and on nucleus lite are as follows.

```bash
# Classic Greengrass nucleus
sudo tail -f /greengrass/v2/logs/com.deepx.dx-runtime.log

# Greengrass nucleus lite
sudo journalctl -f -u ggl.com.deepx.dx-runtime.service
```

> **Note — Installation time**
>
> Installation time varies with device specifications and network conditions. On low-spec arm64 devices that build dependency libraries from source, it can take tens of minutes or more.

To deploy a new driver or runtime version, you use the same approach: increment the component version and create a new deployment for the target thing group. This is why Greengrass is used as an edge operations platform rather than a simple installation tool.

---

## 5. Verifying Deployment and Inference on the Edge Device

When the Greengrass deployment completes, use `dxcli` to check NPU detection status and the firmware version. Then confirm that the dx_stream GStreamer plugin is registered correctly.

```bash
# Check NPU and firmware status
dxcli -s

# Set the dx_stream executable and library paths
GST_ARCH_TRIPLET="$(gcc -dumpmachine 2>/dev/null || true)"
if [ -z "$GST_ARCH_TRIPLET" ]; then
  case "$(uname -m)" in
    x86_64) GST_ARCH_TRIPLET="x86_64-linux-gnu" ;;
    aarch64|arm64) GST_ARCH_TRIPLET="aarch64-linux-gnu" ;;
    armv7l|armv6l) GST_ARCH_TRIPLET="arm-linux-gnueabihf" ;;
    *) GST_ARCH_TRIPLET="$(uname -m)-linux-gnu" ;;
  esac
fi

GST_PLUGIN_DIR="/usr/local/lib/$GST_ARCH_TRIPLET/gstreamer-1.0"
export GST_PLUGIN_PATH="$GST_PLUGIN_DIR:$GST_PLUGIN_PATH"
export LD_LIBRARY_PATH="$GST_PLUGIN_DIR:/usr/local/share/gstdxstream/lib:$LD_LIBRARY_PATH"
export PATH="/usr/local/share/gstdxstream/bin:/usr/local/bin:$PATH"

# Verify the dx_stream GStreamer plugin
gst-inspect-1.0 dxstream
```

The current stack deploys the runtime through Greengrass and stores compiled DXNN models in S3. The following command therefore shows how to download a DXNN model to the device manually for inference verification. To deploy models over the air as well, you need to create a separate Greengrass component that includes the DXNN artifact and the commands to run it.

```bash
aws s3 cp "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/yolov5-s-face_640x640.dxnn" .
```

Next, download a sample video for testing and run inference through the dx_stream pipeline. `dxpreprocess` converts video frames to the model input size (640×640), and `dxinfer` runs inference on the NPU. `dxpostprocess` interprets the detection results using the YOLOv5s-Face post-processing library, `dxosd` draws the bounding boxes on the video, and `fpsdisplaysink` shows the result on screen along with the frame rate.

> **Note — If you change the model**
>
> The post-processing library is model specific. If you use a different model, you must change `library-file-path` to that model's post-processing library along with `model-path`.

```bash
curl -fSLO https://sdk.deepx.ai/res/video/sample_videos.tar.gz
tar xzf sample_videos.tar.gz

export MODEL_PATH="$PWD/yolov5-s-face_640x640.dxnn"
export INPUT_VIDEO_PATH="$PWD/dance-group.mov"
export VIDEOCONVERT_PIPELINE="videoconvert"

gst-launch-1.0 urisourcebin uri=file://$INPUT_VIDEO_PATH ! decodebin ! \
  dxpreprocess preprocess-id=1 resize-width=640 resize-height=640 ! \
  queue max-size-buffers=1 ! \
  dxinfer preprocess-id=1 inference-id=1 model-path=$MODEL_PATH ! \
  queue max-size-buffers=1 ! \
  dxpostprocess inference-id=1 \
  library-file-path=/usr/local/share/gstdxstream/lib/libpostprocess_yolov5s_face.so \
  function-name=PostProcess ! \
  queue max-size-buffers=1 ! dxosd ! \
  $VIDEOCONVERT_PIPELINE ! fpsdisplaysink sync=false
```

![Figure 8. dx_stream face detection result](img/greengrass/fig08_dxstream_result.png)

*Figure 8. Example of face detection running in DEEPX dx_stream*

---

## Cost

AWS resource charges apply separately. See the AWS Marketplace listing for current software pricing and subscription terms, in addition to the following AWS resource usage charges.

- **Amazon EC2**: The compiler instance runs only during a compilation job and is terminated on both success and failure paths, so you are charged only for compilation time.
- **Amazon S3, AWS Lambda, AWS Step Functions, and Amazon CloudWatch Logs**: You incur charges for model file storage, event processing, workflow execution, and log retention.
- **AWS IoT Core and AWS IoT Greengrass**: Charges for device connectivity and deployment operations depend on the features you use and the number of devices.

Actual costs vary with model size, compilation time, Region, number of devices, and log retention period. Before you deploy, estimate costs using the [AWS Pricing Calculator](https://calculator.aws/) and the current pricing for each service.

## Cleaning Up Resources

After you finish, clean up resources in the following order to avoid ongoing charges.

1. Delete the stack in the CloudFormation console. The thing group and component versions created by the stack are removed with it, but a pre-existing group that the stack used is not deleted.
2. The model bucket is retained after stack deletion to protect your data. If you no longer need it, empty the bucket and delete it manually.
3. If you no longer need the AWS Marketplace subscription, cancel it in [Manage subscriptions](https://aws.amazon.com/marketplace/library).
4. (Optional) Revise the deployment in the Greengrass console to remove the component from your devices.

## Conclusion

This document walked through the end-to-end flow of preparing edge AI models and deploying the runtime environment by combining DEEPX DX-M1 series NPUs with AWS IoT services. You used AWS Marketplace and CloudFormation to provision the compilation and deployment resources, and converted an ONNX model uploaded to Amazon S3 into DXNN. You then managed devices with AWS IoT Core things and thing groups and deployed the edge runtime over the air through a Greengrass component.

The value of this combination is not simply that a model runs once on an NPU. It is that artifacts created by model developers are connected to a form that field equipment can execute, and that the same deployment method can be repeated as new equipment and new software versions are added. Once secure provisioning based on the DX-M1 module is connected as well, this can extend to a plug-and-play experience that further reduces field intervention, from AWS IoT Core registration through AWS IoT Greengrass runtime configuration after power and network are connected.

## References

- [DEEPX Greengrass Solution — AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34)
- [DEEPX Compiler Solution — AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo)
- [AWS IoT Core Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html)
- [AWS IoT Greengrass Version 2 Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html)
- [Manage AWS IoT Greengrass deployments](https://docs.aws.amazon.com/greengrass/v2/developerguide/manage-deployments.html)
- [AWS IoT Fleet Provisioning](https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html)
- [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
- [DEEPX Developer Documentation](https://developer.deepx.ai)
- [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/)
- [DEEPX dx-all-suite — GitHub](https://github.com/DEEPX-AI/dx-all-suite)
