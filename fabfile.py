from fabric.api import run, local, sudo, env


@task
def setup():
    sudo('apt-get update')
    sudo('apt-get install python-pip -y')
    sudo('apt-get install mariadb-server -y')
    # pip install MySQL-python on OSX
    sudo('apt-get install python-mysqldb -y')
    sudo('pip install httplib2')
    sudo('pip install jinja2')
    sudo('pip install paypalrestsdk')
    sudo('pip install flask')
    sudo('pip install braintree')
