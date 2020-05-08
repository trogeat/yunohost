import yaml
import sys

app = sys.argv[1]
app_settings_file = "/etc/yunohost/apps/{app}/settings.yml".format(app=app)
app_backup_steps_file = "/etc/yunohost/apps/{app}/backup.yml".format(app=app)

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
# In the output script, let's load all helpers and the relevant settings
#

print("source ../settings/scripts/_common.sh")
print('source /usr/share/yunohost/helpers')
print("")
print("ynh_abort_if_errors")
print("")
print('app={app}'.format(app=app))
for setting, value in app_settings.items():
    print('{setting}="{value}"'.format(setting=setting, value=value))
print("")

#
# Let's load backup.yml
#

backup_steps = yaml.safe_load(open(app_backup_steps_file))

for step in reversed(backup_steps):

    if step.get("cmd"):
        print(step["cmd"])

    if step.get("file"):
        print('ynh_backup --src_path="%s"' % step["file"])

    print("")
