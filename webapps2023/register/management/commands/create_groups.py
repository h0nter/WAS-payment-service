from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from register.models import CustomUser
from payapp.models import Balance, BalanceTransfer
from register.management.user_groups import UserGroups

GROUPS_PERMISSIONS = {
    UserGroups.CUSTOMERS: {
        # Create an empty group without permissions just to identify regular users
    },
    UserGroups.ADMINS: {
        CustomUser: ['view', 'add'],
        Balance: ['view'],
        BalanceTransfer: ['view'],
    }
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:

            print(UserGroups.ADMINS)
            print(UserGroups.CUSTOMERS)

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in \
                        enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write("Adding "
                                          + codename
                                          + " to group "
                                          + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")
