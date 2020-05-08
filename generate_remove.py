import yaml
import sys

app = sys.argv[1]
app_settings_file = "/etc/yunohost/apps/{app}/settings.yml".format(app=app)
app_remove_steps_file = "/etc/yunohost/apps/{app}/remove.yml".format(app=app)

#
# Load settings
#

app_settings = yaml.safe_load(open(app_settings_file))

#
# Filter non-relevant settings
#

ignore_settings = [
    "id",
    "checksum__*",
    "current_revision",
    "install_time",
    "label",
    "unprotected_*",
    "protected_*",
    "skipped_*"
]


def setting_is_ignored(setting):
    # FIXME: Should use proper regexes here
    return setting in ignore_settings or any(setting.startswith(s[:-1]) for s in ignore_settings if s.endswith("_*"))


app_settings = {k: v for k, v in app_settings.items() if not setting_is_ignored(k)}

#
# In the output script, let's load all the relevant settings
#

print('source _common.sh')
print('source /usr/share/yunohost/helpers')
print("")
print('app={app}'.format(app=app))
for setting, value in app_settings.items():
    print('{setting}="{value}"'.format(setting=setting, value=value))
print("")

#
# Let's load remove.yml
#

remove_steps = yaml.safe_load(open(app_remove_steps_file))

# We have to do stuff in reverse (e.g. an nginx conf may expect the
# /var/www/folder to exists which could trigger errors if you remove /var/www/..
# before removing the nginx conf)
for step in reversed(remove_steps):

    if step.get("cmd"):
        print(step["cmd"])

    if step.get("file"):
        print('ynh_secure_remove --file="%s"' % step["file"])

    print("")
