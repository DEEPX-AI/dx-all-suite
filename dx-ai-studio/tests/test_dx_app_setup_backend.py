"""dx_app setup backend: stop, versions, diagnostics i18n."""
import sys, os, tempfile, threading, types, unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# dx_app/core/setup_steps.py does `import config` expecting dx_app/core on sys.path
_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, _root)
sys.path.insert(0, os.path.join(_root, 'dx_app', 'core'))
sys.path.insert(0, os.path.join(_root, 'shared'))

class TestSetupStatus(unittest.TestCase):
    def test_versions_key_in_status(self):
        from dx_app.core.setup_steps import setup_status
        result = setup_status()
        self.assertIn('versions', result)
        v = result['versions']
        self.assertIn('kernel', v)
        self.assertIn('python', v)
        self.assertIsInstance(v['python'], str)
        self.assertRegex(v['python'], r'\d+\.\d+\.\d+')

class TestDeepDiagnosticsI18n(unittest.TestCase):
    def test_labels_are_dicts(self):
        from dx_app.core.setup_steps import deep_diagnostics
        result = deep_diagnostics()
        for check in result['checks']:
            self.assertIsInstance(check['label'], dict, f"{check['id']} label is not dict")
            self.assertIn('en', check['label'])
            self.assertIn('ko', check['label'])

    def test_fix_is_dict_when_present(self):
        from dx_app.core.setup_steps import deep_diagnostics
        result = deep_diagnostics()
        for check in result['checks']:
            if 'fix' in check and check['fix']:
                self.assertIsInstance(check['fix'], dict, f"{check['id']} fix is not dict")

class TestSetupStop(unittest.TestCase):
    def test_stop_no_running_process(self):
        from dx_app.core import setup_steps
        result = setup_steps.setup_stop()
        self.assertFalse(result['ok'])
        self.assertIn('error', result)

class TestSetupDriverEntrypoint(unittest.TestCase):
    def test_driver_step_uses_existing_driver_entrypoint(self):
        from dx_app.core.setup_steps import SETUP_STEPS

        step = SETUP_STEPS['dx-driver']
        script = step['script']()
        self.assertTrue(script.exists(), f"{script} does not exist")
        self.assertEqual(script.name, 'install.sh')
        self.assertIn('--target=dx_rt_npu_linux_driver', step.get('args', []))

    def test_sudo_steps_are_marked_for_preauthorization(self):
        from dx_app.core.setup_steps import SETUP_STEPS

        for step_id in ['dx-app-deps', 'dx-rt-deps', 'dx-driver']:
            self.assertTrue(SETUP_STEPS[step_id].get('needs_sudo'), step_id)

    def test_sudo_preauthorization_uses_stdin_password(self):
        from dx_app.core import setup_steps

        with patch.object(setup_steps.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = ''
            run.return_value.stderr = ''

            error = setup_steps._preauthorize_sudo('secret')

        self.assertIsNone(error)
        run.assert_called_once()
        args, kwargs = run.call_args
        self.assertEqual(args[0], ['sudo', '-S', '-v'])
        self.assertEqual(kwargs['input'], 'secret\n')

    def test_sudo_environment_uses_askpass_for_nested_sudo(self):
        from dx_app.core import setup_steps

        env = {'PATH': '/usr/bin'}
        cleanup = setup_steps._configure_sudo_env(env, 'secret')
        try:
            self.assertIn('SUDO_ASKPASS', env)
            self.assertEqual(env['SUDO_REQUIRE_ASKPASS'], 'force')
            askpass_path = env['SUDO_ASKPASS']
            self.assertTrue(os.path.exists(askpass_path))
            with patch.object(setup_steps.subprocess, 'run') as run:
                run.return_value.returncode = 0
                run.return_value.stdout = ''
                run.return_value.stderr = ''

                error = setup_steps._preauthorize_sudo('secret', env)

            self.assertIsNone(error)
            args, kwargs = run.call_args
            self.assertTrue(args[0][0].endswith('sudo'))
            self.assertEqual(args[0][1:], ['-A', '-v'])
            self.assertIs(kwargs['env'], env)
        finally:
            cleanup()
        self.assertFalse(os.path.exists(askpass_path))

    def test_app_setup_buttons_route_sudo_steps_through_prompt(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        template = open(os.path.join(root, 'dx_app', 'templates', 'index.html'), encoding='utf-8').read()
        script = open(os.path.join(root, 'dx_app', 'static', 'js', 'setup.js'), encoding='utf-8').read()

        self.assertIn("setupRun('dx-driver')", template)
        self.assertIn('SETUP_SUDO_STEPS', script)
        self.assertIn('setupPromptSudoPassword', script)

    def test_completed_setup_step_marks_card_badge_immediately(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        script = open(os.path.join(root, 'dx_app', 'static', 'js', 'setup.js'), encoding='utf-8').read()

        self.assertIn('completedSteps', script)
        self.assertIn('function setupMarkStepDone', script)
        self.assertIn('setupMarkStepDone(completedStep)', script)
        self.assertIn('setupCheckAll().then(function(){setupMarkStepDone(completedStep);});', script)

    def test_sudo_cleanup_runs_when_setup_thread_exits_via_base_exception(self):
        from dx_app.core import setup_steps

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script = temp_path / 'install.sh'
            script.write_text('#!/bin/sh\n', encoding='utf-8')
            script.chmod(0o755)
            password_file = temp_path / 'password'
            cleanup_called = threading.Event()

            def fake_configure_sudo_env(env, password):
                password_file.write_text(password, encoding='utf-8')
                env['SUDO_ASKPASS'] = str(temp_path / 'askpass.sh')

                def cleanup():
                    password_file.unlink(missing_ok=True)
                    cleanup_called.set()

                return cleanup

            def raise_base_exception(*_args, **_kwargs):
                raise SystemExit('daemon thread stopped')

            class SynchronousThread:
                def __init__(self, target, args=(), daemon=None):
                    self.target = target
                    self.args = args

                def start(self):
                    try:
                        self.target(*self.args)
                    except BaseException:
                        pass

            test_step = {
                'script': lambda: script,
                'cwd': lambda: temp_path,
                'args': [],
                'needs_sudo': True,
            }
            with patch.dict(setup_steps.SETUP_STEPS, {'test-sudo-cleanup': test_step}):
                with patch.object(setup_steps, '_configure_sudo_env', fake_configure_sudo_env):
                    with patch.object(setup_steps, '_preauthorize_sudo', return_value=None):
                        with patch.object(setup_steps, '_keep_sudo_alive', return_value=None):
                            with patch.object(setup_steps.subprocess, 'Popen', side_effect=raise_base_exception):
                                with patch.object(setup_steps.threading, 'Thread', SynchronousThread):
                                    result = setup_steps.setup_run('test-sudo-cleanup', {'password': 'secret'})

            self.assertTrue(result['ok'])
            self.assertTrue(cleanup_called.wait(1), 'sudo cleanup was not called')
            self.assertFalse(password_file.exists())

if __name__ == '__main__':
    unittest.main()
