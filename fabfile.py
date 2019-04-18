import os
from fabric import Connection
from fabric.tasks import task
from patchwork.transfers import rsync


USERNAME = os.getenv('USERNAME')
SSH_PASSPHRASE = os.getenv('SSH_PASSPHRASE')
PIPENV = f'/home/{USERNAME}/.local/bin/pipenv'
TARGET_DIRECTORY = os.getenv('TARGET_DIRECTORY', f'/home/{USERNAME}/project-root')


def get_instance_ips():
    """
    Function to get instance IPs of your servers.

    Sometimes you'd want to do this, if your IPs are
    allocated dynamically, e.g. an auto-scaling group
    within AWS.
    """
    return []


def get_hosts():
    """
    Returns a list of dictionaries which can be passed as keyword arguments
    to instantiate a `Connection`.

    Example:
        >>> hosts = get_hosts()
        >>> c = Connection(**hosts[0])
    """
    ips = sorted(get_instance_ips())
    return [{
        'host': f"{USERNAME}@{ip}",
        "connect_kwargs": {"passphrase": SSH_PASSPHRASE},
    } for ip in ips]


@task
def rsync_to_remote(c):
    """
    Does an rsync to the target directory in
    the remote server. Only copies over versioned files
    (ignores everything in `.gitignore`)
    """
    rsync(
        c,
        source="./",
        target=TARGET_DIRECTORY,
        exclude=(".git/",),
        delete=True,
        rsync_opts="--filter=\":- .gitignore\"",
    )


@task
def host_full_deploy(c, migrate=True, collectstatic=True, dependencies=True):
    """
    Full deployment for a host, including migrations and collectstatic
    """
    rsync_to_remote(c)

    with c.cd(TARGET_DIRECTORY):
        if dependencies:
            print("Installing dependencies...\n")
            c.run(f"{PIPENV} install")
        if migrate:
            print("Migrating database...\n")
            c.run(f"{PIPENV} run python manage.py migrate")
        if collectstatic:
            print("Running collectstatic...\n")
            c.run(f"{PIPENV} run python manage.py collectstatic")
        c.run("sudo supervisorctl reload gunicorn")


@task
def deploy(c, migrate=True, dependencies=True, collectstatic=False):
    """
    Main command line task to deploy
    """
    print("START DEPLOYING....")
    for index, host in enumerate(get_hosts()):
        print(f"****** Deploying to host {index} at {host['host']} ******")
        remote = Connection(**host)
        if index == 0:
            host_full_deploy(
                remote,
                migrate=migrate,
                collectstatic=collectstatic,
                dependencies=dependencies,
            )
        else:
            # already migrated and run collectstatic, no need to run again for other hosts
            host_full_deploy(remote, migrate=False, collectstatic=False, dependencies=dependencies)
