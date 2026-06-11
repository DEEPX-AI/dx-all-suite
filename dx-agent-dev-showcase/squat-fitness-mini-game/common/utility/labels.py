"""
Label definitions for common datasets.
"""

from typing import List, Dict

# Label string constants to avoid duplication
_TRAFFIC_LIGHT = "traffic light"
_PARKING_METER = "parking meter"
_HOT_DOG = "hot dog"
_DINING_TABLE = "dining table"
_TEDDY_BEAR = "teddy bear"



def get_coco_80_labels() -> List[str]:
    """
    Get COCO 80-class label names.
    
    Returns:
        List of 80 class names
    """
    return [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
        "boat", _TRAFFIC_LIGHT, "fire hydrant", "stop sign", _PARKING_METER, "bench",
        "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
        "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
        "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
        "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
        "broccoli", "carrot", _HOT_DOG, "pizza", "donut", "cake", "chair", "couch",
        "potted plant", "bed", _DINING_TABLE, "toilet", "tv", "laptop", "mouse",
        "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
        "refrigerator", "book", "clock", "vase", "scissors", _TEDDY_BEAR, "hair drier",
        "toothbrush"
    ]


def get_coco_class_name(class_id: int) -> str:
    """
    Get COCO class name by ID.
    
    Args:
        class_id: Class ID (0-79)
        
    Returns:
        Class name string
    """
    labels = get_coco_80_labels()
    if 0 <= class_id < len(labels):
        return labels[class_id]
    return f"class_{class_id}"


def get_coco_91_labels() -> Dict[int, str]:
    """
    Get COCO 91-class labels with original IDs.
    
    Returns:
        Dictionary mapping class ID to name
    """
    return {
        1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 5: "airplane",
        6: "bus", 7: "train", 8: "truck", 9: "boat", 10: _TRAFFIC_LIGHT,
        11: "fire hydrant", 13: "stop sign", 14: _PARKING_METER, 15: "bench",
        16: "bird", 17: "cat", 18: "dog", 19: "horse", 20: "sheep",
        21: "cow", 22: "elephant", 23: "bear", 24: "zebra", 25: "giraffe",
        27: "backpack", 28: "umbrella", 31: "handbag", 32: "tie", 33: "suitcase",
        34: "frisbee", 35: "skis", 36: "snowboard", 37: "sports ball", 38: "kite",
        39: "baseball bat", 40: "baseball glove", 41: "skateboard", 42: "surfboard",
        43: "tennis racket", 44: "bottle", 46: "wine glass", 47: "cup", 48: "fork",
        49: "knife", 50: "spoon", 51: "bowl", 52: "banana", 53: "apple",
        54: "sandwich", 55: "orange", 56: "broccoli", 57: "carrot", 58: _HOT_DOG,
        59: "pizza", 60: "donut", 61: "cake", 62: "chair", 63: "couch",
        64: "potted plant", 65: "bed", 67: _DINING_TABLE, 70: "toilet", 72: "tv",
        73: "laptop", 74: "mouse", 75: "remote", 76: "keyboard", 77: "cell phone",
        78: "microwave", 79: "oven", 80: "toaster", 81: "sink", 82: "refrigerator",
        84: "book", 85: "clock", 86: "vase", 87: "scissors", 88: _TEDDY_BEAR,
        89: "hair drier", 90: "toothbrush"
    }


def get_cityscapes_labels() -> List[str]:
    """
    Get Cityscapes 19-class labels.
    
    Returns:
        List of 19 class names
    """
    return [
        "road", "sidewalk", "building", "wall", "fence",
        "pole", _TRAFFIC_LIGHT, "traffic sign", "vegetation", "terrain",
        "sky", "person", "rider", "car", "truck",
        "bus", "train", "motorcycle", "bicycle"
    ]


def get_cityscapes_class_name(class_id: int) -> str:
    """
    Get Cityscapes class name by ID.
    
    Args:
        class_id: Class ID (0-18)
        
    Returns:
        Class name string
    """
    labels = get_cityscapes_labels()
    if 0 <= class_id < len(labels):
        return labels[class_id]
    return f"class_{class_id}"


def get_cityscapes_colors() -> List[tuple]:
    """
    Get Cityscapes official colors for visualization.
    
    Returns:
        List of RGB color tuples
    """
    return [
        (128, 64, 128),   # road
        (244, 35, 232),   # sidewalk
        (70, 70, 70),     # building
        (102, 102, 156),  # wall
        (190, 153, 153),  # fence
        (153, 153, 153),  # pole
        (250, 170, 30),   # traffic light
        (220, 220, 0),    # traffic sign
        (107, 142, 35),   # vegetation
        (152, 251, 152),  # terrain
        (70, 130, 180),   # sky
        (220, 20, 60),    # person
        (255, 0, 0),      # rider
        (0, 0, 142),      # car
        (0, 0, 70),       # truck
        (0, 60, 100),     # bus
        (0, 80, 100),     # train
        (0, 0, 230),      # motorcycle
        (119, 11, 32),    # bicycle
    ]


# ImageNet 1000-class labels (full list)
IMAGENET_1000: List[str] = [
    "tench", "goldfish", "great white shark", "tiger shark", "hammerhead shark",
    "electric ray", "stingray", "cock", "hen", "ostrich", "brambling", "goldfinch",
    "house finch", "junco", "indigo bunting", "American robin", "bulbul", "jay",
    "magpie", "chickadee", "American dipper", "kite", "bald eagle", "vulture",
    "great grey owl", "fire salamander", "smooth newt", "newt", "spotted salamander",
    "axolotl", "American bullfrog", "tree frog", "tailed frog", "loggerhead sea turtle",
    "leatherback sea turtle", "mud turtle", "terrapin", "box turtle", "banded gecko",
    "green iguana", "Carolina anole", "desert grassland whiptail lizard", "agama",
    "frilled-necked lizard", "alligator lizard", "Gila monster", "European green lizard",
    "chameleon", "Komodo dragon", "Nile crocodile", "American alligator", "triceratops",
    "worm snake", "ring-necked snake", "eastern hog-nosed snake", "smooth green snake",
    "kingsnake", "garter snake", "water snake", "vine snake", "night snake",
    "boa constrictor", "African rock python", "Indian cobra", "green mamba", "sea snake",
    "Saharan horned viper", "eastern diamondback rattlesnake", "sidewinder", "trilobite",
    "harvestman", "scorpion", "yellow garden spider", "barn spider", "European garden spider",
    "southern black widow", "tarantula", "wolf spider", "tick", "centipede", "black grouse",
    "ptarmigan", "ruffed grouse", "prairie grouse", "peacock", "quail", "partridge",
    "grey parrot", "macaw", "sulphur-crested cockatoo", "lorikeet", "coucal", "bee eater",
    "hornbill", "hummingbird", "jacamar", "toucan", "duck", "red-breasted merganser",
    "goose", "black swan", "tusker", "echidna", "platypus", "wallaby", "koala", "wombat",
    "jellyfish", "sea anemone", "brain coral", "flatworm", "nematode", "conch", "snail",
    "slug", "sea slug", "chiton", "chambered nautilus", "Dungeness crab", "rock crab",
    "fiddler crab", "red king crab", "American lobster", "spiny lobster", "crayfish",
    "hermit crab", "isopod", "white stork", "black stork", "spoonbill", "flamingo",
    "little blue heron", "great egret", "bittern", "crane (bird)", "limpkin",
    "common gallinule", "American coot", "bustard", "ruddy turnstone", "dunlin",
    "common redshank", "dowitcher", "oystercatcher", "pelican", "king penguin", "albatross",
    "grey whale", "killer whale", "dugong", "sea lion", "Chihuahua", "Japanese Chin",
    "Maltese", "Pekingese", "Shih Tzu", "King Charles Spaniel", "Papillon", "toy terrier",
    "Rhodesian Ridgeback", "Afghan Hound", "Basset Hound", "Beagle", "Bloodhound",
    "Bluetick Coonhound", "Black and Tan Coonhound", "Treeing Walker Coonhound",
    "English foxhound", "Redbone Coonhound", "borzoi", "Irish Wolfhound", "Italian Greyhound",
    "Whippet", "Ibizan Hound", "Norwegian Elkhound", "Otterhound", "Saluki",
    "Scottish Deerhound", "Weimaraner", "Staffordshire Bull Terrier",
    "American Staffordshire Terrier", "Bedlington Terrier", "Border Terrier",
    "Kerry Blue Terrier", "Irish Terrier", "Norfolk Terrier", "Norwich Terrier",
    "Yorkshire Terrier", "Wire Fox Terrier", "Lakeland Terrier", "Sealyham Terrier",
    "Airedale Terrier", "Cairn Terrier", "Australian Terrier", "Dandie Dinmont Terrier",
    "Boston Terrier", "Miniature Schnauzer", "Giant Schnauzer", "Standard Schnauzer",
    "Scottish Terrier", "Tibetan Terrier", "Australian Silky Terrier",
    "Soft-coated Wheaten Terrier", "West Highland White Terrier", "Lhasa Apso",
    "Flat-Coated Retriever", "Curly-coated Retriever", "Golden Retriever",
    "Labrador Retriever", "Chesapeake Bay Retriever", "German Shorthaired Pointer",
    "Vizsla", "English Setter", "Irish Setter", "Gordon Setter", "Brittany Spaniel",
    "Clumber Spaniel", "English Springer Spaniel", "Welsh Springer Spaniel",
    "Cocker Spaniels", "Sussex Spaniel", "Irish Water Spaniel", "Kuvasz", "Schipperke",
    "Groenendael", "Malinois", "Briard", "Australian Kelpie", "Komondor",
    "Old English Sheepdog", "Shetland Sheepdog", "collie", "Border Collie",
    "Bouvier des Flandres", "Rottweiler", "German Shepherd Dog", "Dobermann",
    "Miniature Pinscher", "Greater Swiss Mountain Dog", "Bernese Mountain Dog",
    "Appenzeller Sennenhund", "Entlebucher Sennenhund", "Boxer", "Bullmastiff",
    "Tibetan Mastiff", "French Bulldog", "Great Dane", "St. Bernard", "husky",
    "Alaskan Malamute", "Siberian Husky", "Dalmatian", "Affenpinscher", "Basenji",
    "pug", "Leonberger", "Newfoundland", "Pyrenean Mountain Dog", "Samoyed",
    "Pomeranian", "Chow Chow", "Keeshond", "Griffon Bruxellois", "Pembroke Welsh Corgi",
    "Cardigan Welsh Corgi", "Toy Poodle", "Miniature Poodle", "Standard Poodle",
    "Mexican hairless dog", "grey wolf", "Alaskan tundra wolf", "red wolf", "coyote",
    "dingo", "dhole", "African wild dog", "hyena", "red fox", "kit fox", "Arctic fox",
    "grey fox", "tabby cat", "tiger cat", "Persian cat", "Siamese cat", "Egyptian Mau",
    "cougar", "lynx", "leopard", "snow leopard", "jaguar", "lion", "tiger", "cheetah",
    "brown bear", "American black bear", "polar bear", "sloth bear", "mongoose", "meerkat",
    "tiger beetle", "ladybug", "ground beetle", "longhorn beetle", "leaf beetle",
    "dung beetle", "rhinoceros beetle", "weevil", "fly", "bee", "ant", "grasshopper",
    "cricket", "stick insect", "cockroach", "mantis", "cicada", "leafhopper", "lacewing",
    "dragonfly", "damselfly", "red admiral", "ringlet", "monarch butterfly", "small white",
    "sulphur butterfly", "gossamer-winged butterfly", "starfish", "sea urchin",
    "sea cucumber", "cottontail rabbit", "hare", "Angora rabbit", "hamster", "porcupine",
    "fox squirrel", "marmot", "beaver", "guinea pig", "common sorrel", "zebra", "pig",
    "wild boar", "warthog", "hippopotamus", "ox", "water buffalo", "bison", "ram",
    "bighorn sheep", "Alpine ibex", "hartebeest", "impala", "gazelle", "dromedary",
    "llama", "weasel", "mink", "European polecat", "black-footed ferret", "otter",
    "skunk", "badger", "armadillo", "three-toed sloth", "orangutan", "gorilla",
    "chimpanzee", "gibbon", "siamang", "guenon", "patas monkey", "baboon", "macaque",
    "langur", "black-and-white colobus", "proboscis monkey", "marmoset",
    "white-headed capuchin", "howler monkey", "titi", "Geoffroy's spider monkey",
    "common squirrel monkey", "ring-tailed lemur", "indri", "Asian elephant",
    "African bush elephant", "red panda", "giant panda", "snoek", "eel", "coho salmon",
    "rock beauty", "clownfish", "sturgeon", "garfish", "lionfish", "pufferfish",
    "abacus", "abaya", "academic gown", "accordion", "acoustic guitar", "aircraft carrier",
    "airliner", "airship", "altar", "ambulance", "amphibious vehicle", "analog clock",
    "apiary", "apron", "waste container", "assault rifle", "backpack", "bakery",
    "balance beam", "balloon", "ballpoint pen", "Band-Aid", "banjo", "baluster",
    "barbell", "barber chair", "barbershop", "barn", "barometer", "barrel", "wheelbarrow",
    "baseball", "basketball", "bassinet", "bassoon", "swimming cap", "bath towel",
    "bathtub", "station wagon", "lighthouse", "beaker", "military cap", "beer bottle",
    "beer glass", "bell-cot", "bib", "tandem bicycle", "bikini", "ring binder",
    "binoculars", "birdhouse", "boathouse", "bobsleigh", "bolo tie", "poke bonnet",
    "bookcase", "bookstore", "bottle cap", "bow", "bow tie", "brass", "bra", "breakwater",
    "breastplate", "broom", "bucket", "buckle", "bulletproof vest", "high-speed train",
    "butcher shop", "taxicab", "cauldron", "candle", "cannon", "canoe", "can opener",
    "cardigan", "car mirror", "carousel", "tool kit", "carton", "car wheel",
    "automated teller machine", "cassette", "cassette player", "castle", "catamaran",
    "CD player", "cello", "mobile phone", "chain", "chain-link fence", "chain mail",
    "chainsaw", "chest", "chiffonier", "chime", "china cabinet", "Christmas stocking",
    "church", "movie theater", "cleaver", "cliff dwelling", "cloak", "clogs",
    "cocktail shaker", "coffee mug", "coffeemaker", "coil", "combination lock",
    "computer keyboard", "confectionery store", "container ship", "convertible",
    "corkscrew", "cornet", "cowboy boot", "cowboy hat", "cradle", "crane (machine)",
    "crash helmet", "crate", "infant bed", "Crock Pot", "croquet ball", "crutch",
    "cuirass", "dam", "desk", "desktop computer", "rotary dial telephone", "diaper",
    "digital clock", "digital watch", _DINING_TABLE, "dishcloth", "dishwasher",
    "disc brake", "dock", "dog sled", "dome", "doormat", "drilling rig", "drum",
    "drumstick", "dumbbell", "Dutch oven", "electric fan", "electric guitar",
    "electric locomotive", "entertainment center", "envelope", "espresso machine",
    "face powder", "feather boa", "filing cabinet", "fireboat", "fire engine",
    "fire screen sheet", "flagpole", "flute", "folding chair", "football helmet",
    "forklift", "fountain", "fountain pen", "four-poster bed", "freight car",
    "French horn", "frying pan", "fur coat", "garbage truck", "gas mask", "gas pump",
    "goblet", "go-kart", "golf ball", "golf cart", "gondola", "gong", "gown",
    "grand piano", "greenhouse", "grille", "grocery store", "guillotine", "barrette",
    "hair spray", "half-track", "hammer", "hamper", "hair dryer", "hand-held computer",
    "handkerchief", "hard disk drive", "harmonica", "harp", "harvester", "hatchet",
    "holster", "home theater", "honeycomb", "hook", "hoop skirt", "horizontal bar",
    "horse-drawn vehicle", "hourglass", "iPod", "clothes iron", "jack-o'-lantern",
    "jeans", "jeep", "T-shirt", "jigsaw puzzle", "pulled rickshaw", "joystick",
    "kimono", "knee pad", "knot", "lab coat", "ladle", "lampshade", "laptop computer",
    "lawn mower", "lens cap", "paper knife", "library", "lifeboat", "lighter",
    "limousine", "ocean liner", "lipstick", "slip-on shoe", "lotion", "speaker",
    "loupe", "sawmill", "magnetic compass", "mail bag", "mailbox", "tights",
    "tank suit", "manhole cover", "maraca", "marimba", "mask", "match", "maypole",
    "maze", "measuring cup", "medicine chest", "megalith", "microphone", "microwave oven",
    "military uniform", "milk can", "minibus", "miniskirt", "minivan", "missile",
    "mitten", "mixing bowl", "mobile home", "Model T", "modem", "monastery", "monitor",
    "moped", "mortar", "square academic cap", "mosque", "mosquito net", "scooter",
    "mountain bike", "tent", "computer mouse", "mousetrap", "moving van", "muzzle",
    "nail", "neck brace", "necklace", "nipple", "notebook computer", "obelisk", "oboe",
    "ocarina", "odometer", "oil filter", "organ", "oscilloscope", "overskirt",
    "bullock cart", "oxygen mask", "packet", "paddle", "paddle wheel", "padlock",
    "paintbrush", "pajamas", "palace", "pan flute", "paper towel", "parachute",
    "parallel bars", "park bench", _PARKING_METER, "passenger car", "patio", "payphone",
    "pedestal", "pencil case", "pencil sharpener", "perfume", "Petri dish", "photocopier",
    "plectrum", "Pickelhaube", "picket fence", "pickup truck", "pier", "piggy bank",
    "pill bottle", "pillow", "ping-pong ball", "pinwheel", "pirate ship", "pitcher",
    "hand plane", "planetarium", "plastic bag", "plate rack", "plow", "plunger",
    "Polaroid camera", "pole", "police van", "poncho", "billiard table", "soda bottle",
    "pot", "potter's wheel", "power drill", "prayer rug", "printer", "prison",
    "projectile", "projector", "hockey puck", "punching bag", "purse", "quill", "quilt",
    "race car", "racket", "radiator", "radio", "radio telescope", "rain barrel",
    "recreational vehicle", "reel", "reflex camera", "refrigerator", "remote control",
    "restaurant", "revolver", "rifle", "rocking chair", "rotisserie", "eraser",
    "rugby ball", "ruler", "running shoe", "safe", "safety pin", "salt shaker",
    "sandal", "sarong", "saxophone", "scabbard", "weighing scale", "school bus",
    "schooner", "scoreboard", "CRT screen", "screw", "screwdriver", "seat belt",
    "sewing machine", "shield", "shoe store", "shoji", "shopping basket", "shopping cart",
    "shovel", "shower cap", "shower curtain", "ski", "ski mask", "sleeping bag",
    "slide rule", "sliding door", "slot machine", "snorkel", "snowmobile", "snowplow",
    "soap dispenser", "soccer ball", "sock", "solar thermal collector", "sombrero",
    "soup bowl", "space bar", "space heater", "space shuttle", "spatula", "motorboat",
    "spider web", "spindle", "sports car", "spotlight", "stage", "steam locomotive",
    "through arch bridge", "steel drum", "stethoscope", "scarf", "stone wall",
    "stopwatch", "stove", "strainer", "tram", "stretcher", "couch", "stupa", "submarine",
    "suit", "sundial", "sunglass", "sunglasses", "sunscreen", "suspension bridge", "mop",
    "sweatshirt", "swimsuit", "swing", "switch", "syringe", "table lamp", "tank",
    "tape player", "teapot", _TEDDY_BEAR, "television", "tennis ball", "thatched roof",
    "front curtain", "thimble", "threshing machine", "throne", "tile roof", "toaster",
    "tobacco shop", "toilet seat", "torch", "totem pole", "tow truck", "toy store",
    "tractor", "semi-trailer truck", "tray", "trench coat", "tricycle", "trimaran",
    "tripod", "triumphal arch", "trolleybus", "trombone", "tub", "turnstile",
    "typewriter keyboard", "umbrella", "unicycle", "upright piano", "vacuum cleaner",
    "vase", "vault", "velvet", "vending machine", "vestment", "viaduct", "violin",
    "volleyball", "waffle iron", "wall clock", "wallet", "wardrobe", "military aircraft",
    "sink", "washing machine", "water bottle", "water jug", "water tower", "whiskey jug",
    "whistle", "wig", "window screen", "window shade", "Windsor tie", "wine bottle",
    "wing", "wok", "wooden spoon", "wool", "split-rail fence", "shipwreck", "yawl",
    "yurt", "website", "comic book", "crossword", "traffic sign", _TRAFFIC_LIGHT,
    "dust jacket", "menu", "plate", "guacamole", "consomme", "hot pot", "trifle",
    "ice cream", "ice pop", "baguette", "bagel", "pretzel", "cheeseburger", _HOT_DOG,
    "mashed potato", "cabbage", "broccoli", "cauliflower", "zucchini", "spaghetti squash",
    "acorn squash", "butternut squash", "cucumber", "artichoke", "bell pepper", "cardoon",
    "mushroom", "Granny Smith", "strawberry", "orange", "lemon", "fig", "pineapple",
    "banana", "jackfruit", "custard apple", "pomegranate", "hay", "carbonara",
    "chocolate syrup", "dough", "meatloaf", "pizza", "pot pie", "burrito", "red wine",
    "espresso", "cup", "eggnog", "alp", "bubble", "cliff", "coral reef", "geyser",
    "lakeshore", "promontory", "shoal", "seashore", "valley", "volcano", "baseball player",
    "bridegroom", "scuba diver", "rapeseed", "daisy", "yellow lady's slipper", "corn",
    "acorn", "rose hip", "horse chestnut seed", "coral fungus", "agaric", "gyromitra",
    "stinkhorn mushroom", "earth star", "hen-of-the-woods", "bolete", "ear of corn",
    "toilet paper",
]


def get_imagenet_labels() -> List[str]:
    """
    Get ImageNet 1000-class labels.
    
    Returns:
        List of 1000 ImageNet class names
    """
    return IMAGENET_1000.copy()


# Dataset name to label mapping
def get_voc_labels() -> List[str]:
    """Pascal VOC 20 class labels."""
    return [
        "aeroplane", "bicycle", "bird", "boat", "bottle",
        "bus", "car", "cat", "chair", "cow",
        "diningtable", "dog", "horse", "motorbike", "person",
        "pottedplant", "sheep", "sofa", "train", "tvmonitor",
    ]


_DATASET_LABELS: Dict[str, List[str]] = {
    "coco80": get_coco_80_labels(),
    "imagenet1000": get_imagenet_labels(),
    "cityscapes": get_cityscapes_labels(),
    "voc": get_voc_labels(),
    "palm": ["palm"],
}


def get_labels(dataset_name: str) -> List[str]:
    """
    Get labels by dataset name.
    
    Args:
        dataset_name: Dataset name (e.g., "coco80")
        
    Returns:
        List of class names
        
    Raises:
        ValueError: If dataset name is unknown
    """
    key = dataset_name.lower()
    if key not in _DATASET_LABELS:
        available = ", ".join(sorted(_DATASET_LABELS.keys()))
        raise ValueError(
            f"Unknown dataset labels: {dataset_name}. Available: {available}"
        )
    return _DATASET_LABELS[key]
