# Lab setup guide

How to get the network compliance lab running on your machine and start working on it.

## 1. Prerequisites

- An **Apple Silicon Mac** (these steps), or an x86 Linux machine (see notes in step 4).
- At least 16 GB RAM. The lab uses about 6 GB.
- A GitHub account with collaborator access to this repo.
- A free **Arista account** (arista.com), needed to download the Arista image yourself.

## 2. Install the tools (Mac)

1. Update macOS, and turn on FileVault and the firewall.
2. Install Apple's developer tools: `xcode-select --install`
3. Install Homebrew from https://brew.sh (download the script, read it, then run it).
4. Install OrbStack: `brew install --cask orbstack`, then open it.
   - The free tier is personal use only. Business use needs OrbStack Pro.
   - In OrbStack settings, set memory to at least 8 GB.
5. Create the Linux machine and open a shell in it:

```bash
   orb create ubuntu clab
   orb -m clab
   cd ~
```

   **Everything from here runs inside this Linux machine.**

6. Update it and install Docker and containerlab:

```bash
   sudo apt update && sudo apt -y upgrade
   curl -sL -o /tmp/clab-setup.sh https://containerlab.dev/setup
   less /tmp/clab-setup.sh            # review it
   sudo -E bash /tmp/clab-setup.sh all
   sudo usermod -aG docker $USER
   exit                               # then reopen with: orb -m clab
   docker run --rm hello-world && containerlab version
```

## 3. Get the repo

Use an SSH key (fine-grained tokens can't access a repo owned by another personal account):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
ssh-keygen -t ed25519 -C "you@example.com"      # set a passphrase
cat ~/.ssh/id_ed25519.pub                       # add this at GitHub → Settings → SSH and GPG keys
ssh -T git@github.com                           # should greet you by username

mkdir -p ~/netlab && cd ~/netlab
git clone git@github.com:princesoin/illuminare-networks-network-compliance-lab.git repo
cd repo
```

## 4. Get the images

The lab uses these images (check `grep image: labs/dev/dev-topology.clab.yml` for the exact versions):

| Image | How to get it |
|-------|---------------|
| Nokia SR Linux | Pulled automatically by containerlab |
| FRRouting | Pulled automatically by containerlab |
| Alpine | Pulled automatically by containerlab |
| Arista cEOS 4.36.2F | **Manual download.** Its licence doesn't allow it in Git. |

**Arista (manual):**

1. On arista.com → Software Downloads → EOS → cEOS-lab → 4.36 → EOS-4.36.2F, download:
   - `cEOSarm-lab-4.36.2F.tar.xz` (Apple Silicon), or `cEOS64-lab-4.36.2F.tar.xz` (x86 Linux)
   - the matching `.sha512sum` file
2. Verify it on your Mac:

```bash
   cd ~/Downloads
   shasum -a 512 -c cEOSarm-lab-4.36.2F.tar.xz.sha512sum     # must print OK
```

3. Copy it into the Linux machine (run on the Mac):

```bash
   orb push -m clab ~/Downloads/cEOSarm-lab-4.36.2F.tar.xz /home/<your-linux-user>/
```

4. Import it **with exactly this tag**, so it matches the topology:

```bash
   cd ~
   docker import cEOSarm-lab-4.36.2F.tar.xz ceos:4.36.2F
   docker image inspect ceos:4.36.2F --format '{{.Architecture}}'   # arm64 on Mac
   rm cEOSarm-lab-4.36.2F.tar.xz
```

   Use `docker import`, not `docker load`.

## 5. Run the lab

```bash
cd ~/netlab/repo/labs/dev
sudo containerlab deploy -t dev-topology.clab.yml
sudo containerlab inspect -t dev-topology.clab.yml
```

Give Arista 2–3 minutes to boot. Then check:

```bash
docker exec -it clab-dev-topology-ceos1 Cli -c "ping 10.0.14.2"
docker exec -it clab-dev-topology-srl1 sr_cli "ping 10.0.12.2 network-instance default -c 3"
```

Logins (lab only): Arista `admin` / `admin`, SR Linux `admin` / `NokiaSrl1!`, and FRR via
`docker exec -it clab-dev-topology-frr1 vtysh`.

Stop the lab when you're done:

```bash
sudo containerlab destroy -t dev-topology.clab.yml --cleanup
```

## 6. Ansible (optional, for playbooks)

```bash
cd ~/netlab
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip ansible
ansible-galaxy collection install nokia.srlinux
```

The vault file isn't in Git. Create your own with the lab password:

```bash
cd ~/netlab/repo
ansible-vault create ansible/inventory/group_vars/srlinux/vault.yml
# add:  vault_srl_password: NokiaSrl1!
ansible-playbook ansible/playbooks/check-srl.yml --ask-vault-pass
```

## 7. How we work together

- **Pull before you start:** `git pull --rebase`
- **Use a branch for each piece of work:**

```bash
  git checkout -b feature/short-description
  # make changes, test the lab
  git add . && git status        # check nothing sensitive is staged
  git commit -m "Clear description of the change"
  git push -u origin feature/short-description
```

  Then open a pull request on GitHub for the other person to review.
- **Configs are file-first:** change the files in `labs/*/configs/`, then destroy and redeploy. Live CLI changes are lost unless copied back into the files.
- **Every new link needs both ends configured:** a new /30 subnet, `.1` on one device and `.2` on the other.

## 8. Never commit

- Vault files, passwords, tokens or keys
- Vendor images (`*.tar.xz`, `*.tgz`) or licence files (`*.lic`)
- Generated lab folders (`clab-*`) or `.venv`
- Real client data or configs of any kind

`.gitignore` covers most of these, but always check `git status` before committing.

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| `exec format error` | Wrong architecture: use the `cEOSarm` image on Apple Silicon |
| `invalid reference format` | An image tag in the topology is wrong or a placeholder |
| Arista image "not found" at deploy | It wasn't imported as exactly `ceos:4.36.2F` |
| SR Linux won't accept changes | Use `enter candidate`, then `commit now` |
| SSH refused to Arista | Still booting: wait, or use `docker exec ... Cli` |
| Containers stop, or everything is slow | Raise OrbStack's memory and close other apps |
| `cd: no such file` after opening the machine | The shell started in a Mac folder: `cd ~/netlab/repo` |
