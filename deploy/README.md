# Ansible setup

1. Install ansible: `pip install ansible`
2. Clone the git repo: `git clone https://github.com/appsembler/launcher.git`
3. Enter the deploy folder: `cd deploy`
4. Enter the IP address of the servers under `[launcher]` and `[docker]` in the file production in `hosts/production` folder
5. Copy the secret keys template and fill in secret keys in the `secret_vars.yml` file: `cp secret_vars.yml.example secret_vars.yml`
6. Run the ansible scripts: `ansible-playbook -i hosts/production/inventory site.yml`
