skill_mappings = {
    # Web Development
    "html": {"css": 0.9, "javascript": 0.8, "bootstrap": 0.7, "tailwindcss": 0.75, "markdown": 0.7},
    "css": {"sass": 0.8, "tailwindcss": 0.85, "bootstrap": 0.8, "materialize": 0.75, "bulma": 0.7},
    "javascript": {"react": 0.9, "vue": 0.85, "angular": 0.8, "node.js": 0.8, "jquery": 0.7, "d3.js": 0.75, "three.js": 0.7},
    "react": {"redux": 0.85, "next.js": 0.9, "typescript": 0.8, "material-ui": 0.8, "react-router": 0.8},
    "vue": {"vuex": 0.85, "nuxt.js": 0.8, "typescript": 0.8, "quasar": 0.75, "pinia": 0.75},
    "angular": {"rxjs": 0.85, "typescript": 0.9, "ngrx": 0.8, "prime-ng": 0.75, "angular_material": 0.8},
    "node.js": {"express": 0.9, "nest.js": 0.85, "graphql": 0.8, "koa": 0.75, "hapi": 0.7},
    "tailwindcss": {"postcss": 0.8, "next.js": 0.85, "daisyui": 0.75, "flowbite": 0.7},
    "bootstrap": {"jquery": 0.7, "sass": 0.75, "popper.js": 0.7, "foundation": 0.7},

    # AI/ML
    "python": {"numpy": 0.9, "pandas": 0.9, "tensorflow": 0.85, "pytorch": 0.85, "scipy": 0.8, "matplotlib": 0.8, "seaborn": 0.75},
    "tensorflow": {"keras": 0.9, "opencv": 0.8, "scikit-learn": 0.8, "tflite": 0.75, "tensorboard": 0.7},
    "pytorch": {"torchvision": 0.9, "transformers": 0.85, "scikit-learn": 0.8, "onnx": 0.75, "pytorch_lightning": 0.8},
    "scikit-learn": {"xgboost": 0.85, "lightgbm": 0.8, "mlflow": 0.7, "catboost": 0.75, "joblib": 0.7},
    "nlp": {"spacy": 0.85, "transformers": 0.9, "nltk": 0.8, "gpt": 0.9, "fasttext": 0.75, "sentence_transformers": 0.8},
    "computer_vision": {"opencv": 0.9, "dlib": 0.8, "mediapipe": 0.85, "yolov5": 0.8, "detectron2": 0.75, "mmcv": 0.75},
    "deep_learning": {"tensorflow": 0.9, "pytorch": 0.9, "mxnet": 0.75, "caffe": 0.7, "deeplearning4j": 0.7},

    # DevOps
    "docker": {"kubernetes": 0.9, "ansible": 0.8, "terraform": 0.8, "podman": 0.75, "docker_compose": 0.8},
    "kubernetes": {"helm": 0.85, "istio": 0.8, "argo": 0.75, "prometheus": 0.8, "kustomize": 0.75},
    "ansible": {"jenkins": 0.8, "terraform": 0.75, "chef": 0.7, "saltstack": 0.7},
    "terraform": {"aws": 0.9, "gcp": 0.85, "azure": 0.85, "digitalocean": 0.75, "linode": 0.7},
    "aws": {"ec2": 0.9, "s3": 0.9, "lambda": 0.85, "cloudfront": 0.8, "dynamodb": 0.8, "rds": 0.8},
    "gcp": {"compute_engine": 0.9, "cloud_run": 0.85, "bigquery": 0.8, "firebase": 0.85, "pubsub": 0.75},
    "ci_cd": {"jenkins": 0.9, "circleci": 0.85, "github_actions": 0.8, "gitlab_ci": 0.8, "travis_ci": 0.75},

    # Web3
    "solidity": {"hardhat": 0.85, "truffle": 0.8, "ethers.js": 0.8, "remix": 0.75, "open_zeppelin": 0.8},
    "web3.js": {"ethers.js": 0.85, "alchemy": 0.8, "infura": 0.8, "ganache": 0.75, "web3_py": 0.75},
    "ethers.js": {"hardhat": 0.85, "truffle": 0.8, "wagmi": 0.8, "web3modal": 0.7},
    "hardhat": {"chai": 0.85, "mocha": 0.8, "waffle": 0.75, "solhint": 0.7},
    "nfts": {"opensea": 0.85, "rarible": 0.8, "ipfs": 0.85, "pinata": 0.75, "mintbase": 0.75},

    # App Development
    "flutter": {"dart": 0.9, "firebase": 0.85, "bloc": 0.8, "riverpod": 0.75, "getx": 0.75},
    "react_native": {"javascript": 0.9, "typescript": 0.85, "expo": 0.8, "redux": 0.8},
    "dart": {"flutter": 0.9, "firebase": 0.85, "angular_dart": 0.75, "stagehand": 0.7},

    # iOS Development
    "swift": {"xcode": 0.9, "core_data": 0.85, "swift_ui": 0.8, "combine": 0.75, "cocoa_pods": 0.8},
    "objective_c": {"xcode": 0.85, "cocoapods": 0.8, "foundation_framework": 0.8, "appkit": 0.75},

    # Android Development
    "kotlin": {"android_studio": 0.9, "jetpack_compose": 0.85, "firebase": 0.85, "ktor": 0.8, "dagger_hilt": 0.8, "android_sdk": 0.9},
    "java": {"android_studio": 0.9, "spring": 0.8, "hibernate": 0.8, "struts": 0.75},

    # Cyber Security
    "penetration_testing": {"metasploit": 0.9, "burpsuite": 0.85, "owasp": 0.8, "kali_linux": 0.9, "nmap": 0.8},
    "network_security": {"wireshark": 0.9, "firewalls": 0.85, "vpn": 0.8, "ids_ips": 0.75, "tls_ssl": 0.8},
    "cryptography": {"rsa": 0.9, "aes": 0.85, "hashing": 0.8, "ecc": 0.8, "pgp": 0.75},

    # Computer Networking
    "networking_basics": {"tcp_ip": 0.9, "udp": 0.85, "dhcp": 0.8, "dns": 0.8, "ipv6": 0.75},
    "advanced_networking": {"bgp": 0.85, "ospf": 0.8, "vpn": 0.8, "load_balancers": 0.75, "qos": 0.7},
    "cloud_networking": {"vpc": 0.9, "load_balancing": 0.85, "cdn": 0.8, "direct_connect": 0.75},

    # Project Management
    "agile_methodologies": {"scrum": 0.9, "kanban": 0.85, "safe": 0.8, "lean": 0.8, "jira": 0.85},
    "project_lifecycle": {"planning": 0.9, "execution": 0.85, "monitoring": 0.8, "closure": 0.75},
    "tools": {"ms_project": 0.85, "asana": 0.8, "trello": 0.8, "clickup": 0.75},

    # Testing
    "manual_testing": {"test_cases": 0.9, "test_plan": 0.85, "bug_tracking": 0.8, "qa": 0.8},
    "automation_testing": {"selenium": 0.9, "junit": 0.85, "pytest": 0.8, "cypress": 0.75, "appium": 0.8},
    "performance_testing": {"jmeter": 0.9, "gatling": 0.85, "blazemeter": 0.8},

    # Marketing
    "seo": {"on_page_seo": 0.9, "off_page_seo": 0.85, "technical_seo": 0.8, "content_seo": 0.75},
    "digital_marketing": {"google_ads": 0.9, "facebook_ads": 0.85, "linkedin_ads": 0.8, "email_marketing": 0.8},
    "analytics": {"google_analytics": 0.9, "mixpanel": 0.85, "hotjar": 0.8, "kissmetrics": 0.75},

    # High-Level Skills
    "full_stack_development": {"frontend_development": 0.9, "backend_development": 0.9, "database_management": 0.85, "api_design": 0.8},
    "frontend_development": {"react": 0.9, "vue": 0.85, "angular": 0.8, "svelte": 0.8, "backbone.js": 0.7},
    "backend_development": {"node.js": 0.9, "django": 0.85, "flask": 0.8, "spring_boot": 0.85, "laravel": 0.8},
    "database_management": {"mongodb": 0.85, "mysql": 0.8, "postgresql": 0.8, "redis": 0.75, "cassandra": 0.7},
    "cloud_computing": {"aws": 0.9, "gcp": 0.85, "azure": 0.85, "digitalocean": 0.8, "openstack": 0.75},

    # Deep Level Skills
    "graphql": {"apollo_client": 0.9, "relay": 0.85, "hasura": 0.8, "prisma": 0.8, "dataloader": 0.75},
    "api_design": {"rest": 0.9, "graphql": 0.85, "grpc": 0.8, "soap": 0.7, "openapi": 0.75},
    "data_structures": {"arrays": 0.9, "linked_lists": 0.85, "hash_maps": 0.85, "binary_trees": 0.8, "graphs": 0.8},
    "algorithms": {"sorting": 0.9, "searching": 0.85, "dynamic_programming": 0.85, "greedy_algorithms": 0.8, "backtracking": 0.8},

    # Cross-Domain Connections
    "webdev_to_web3": {"react": 0.85, "ethers.js": 0.8, "graphql": 0.8, "node.js": 0.85},
    "web3_to_ai": {"python": 0.85, "tensorflow": 0.8, "pytorch": 0.8, "data_structures": 0.75},
    "ai_to_devops": {"docker": 0.85, "kubernetes": 0.8, "terraform": 0.75},
    "devops_to_app_dev": {"flutter": 0.85, "react_native": 0.8, "firebase": 0.8},
    "ios_to_android": {"swift": 0.8, "kotlin": 0.8, "java": 0.75},
    "cybersecurity_to_networking": {"penetration_testing": 0.85, "networking_basics": 0.8, "advanced_networking": 0.75},
    "project_management_to_testing": {"agile_methodologies": 0.85, "manual_testing": 0.8, "automation_testing": 0.75},
    "testing_to_marketing": {"analytics": 0.85, "seo": 0.8, "performance_testing": 0.75}
}
