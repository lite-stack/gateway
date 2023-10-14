def get_os_default_user(image: str):
    match image.split("-"):
        case ["cirros", *_, ]:
            return "cirros"
        case ["ubuntu", *_,]:
            return "ubuntu"
        case ["centos", *_]:
            return "centos"
        case ["debian", *_]:
            return "debian"
        case ["fedora", *_]:
            return "fedora"
        case ["arch", *_]:
            return "arch"
        case _:
            return "root"