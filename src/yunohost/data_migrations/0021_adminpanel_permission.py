
from moulinette import m18n
from moulinette.utils.log import getActionLogger
from moulinette.utils.filesystem import read_yaml

from yunohost.tools import Migration
from yunohost.permission import user_permission_update

logger = getActionLogger('yunohost.migration')

###################################################
# Tools used also for restoration
###################################################


class MyMigration(Migration):
    """
        Add new permissions to access Admin Panel
    """

    required = True

    def run(self):
        logger.info(m18n.n("migration_0021_adminpanel_permission"))

        from yunohost.utils.ldap import _get_ldap_interface
        ldap = _get_ldap_interface()

        add_perm_to_users = False

        # Add Admin Panel permission
        ldap_map = read_yaml('/usr/share/yunohost/yunohost-config/moulinette/ldap_scheme.yml')
        for rdn, attr_dict in ldap_map['depends_children'].items():
            try:
                ldap.search(rdn + ",dc=yunohost,dc=org")
            # ldap search will raise an exception if no corresponding object is found >.> ...
            except Exception:
                if rdn == "cn=adminpanel.main,ou=permission":
                    add_perm_to_users = True
                ldap.add(rdn, attr_dict)

        # Add perm to each users ? FIX TODO
        users = ldap.search('ou=users,dc=yunohost,dc=org', filter="(uid=*)", attrs=["dn", "uid", "loginShell"])
        for user in users:
            if add_perm_to_users:
                user_permission_update("adminpanel.main", add=user["uid"][0], sync_perm=False)

