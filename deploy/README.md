# Ansible setup

1. Install ansible: `pip install ansible`
2. Clone the git repo: `git clone https://github.com/appsembler/mediathread.git`
3. Switch to the ansible branch: `git checkout feature/ansible`
4. Enter the deploy folder: `cd deploy`
5. Enter the IP address of the server under `[server]` in the file production in the current folder
6. Copy the secret keys template and fill in secret keys in the `secret_vars.yml` file: `cp secret_vars.yml.example secret_vars.yml`
7. Run the ansible scripts: `ansible-playbook -i production site.yml`
