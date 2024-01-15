

class Role:
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"

    ROLE_CHOICES = [
        (ADMIN, "admin"),
        (MANAGER, "manager"),
        (WORKER, "worker"),
    ]
