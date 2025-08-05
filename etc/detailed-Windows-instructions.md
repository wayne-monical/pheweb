
## Using Pheweb on Windows

Pheweb can be run on Windows using Windows Subsystem for Linux, a program that creates a Linux virtual machine, which can then run Pheweb and its dependencies. 

1. Install WSL2 from the Microsoft Store.
2. In the WSL terminal, install the necessary C libraries for Pheweb.


```{wsl}
sudo apt update
sudo apt install g++
sudo apt install zlib1g-dev 
```

3. Install conda by downloading the latest conda installer, then run the following code

```{wsl}
bash Miniconda3-latest-Linux-x86_64.sh 
```

4. Create a new conda environment for pheweb

```{wsl}
conda create --name phewas python=3.10.0 
```

5. Install your preferred version of pheweb. 

```
conda activate phewas
conda config --add channels conda-forge
conda install bioconda::pysam=0.22.1
pip install --use-pep517 git+https://github.com/wayne-monical/pheweb.git 
```


6. Copy the input data from the Windows file system to the Linux file system.

7. Create a directory for the pheweb project. Assemble the the association files as csvs and the pheno-list file as a csv or as a json in the directory, and run the pheweb commands as usual.

```
# import list of phenotypes
pheweb phenolist import-phenolist pheno-list.csv

# process data
pheweb process

# serve website
pheweb serve
```



## Port Forwarding with WSL

Pheweb can be hosted on your computer and made available via port forwarding. However, the website will only be accessible while your computer is on and running the Pheweb program. 

1. When running the website, consider hosting at the 55000 port as opposed to the default 5000 port, because the 5000 port may be blocked by an ISP. The website will be viewable by you (but not anyone else) at http://localhost:55000.

```{wsl}
pheweb serve --host 0.0.0.0 --port 55000
```

2. Publishing the Website with Port Forwarding

When a member of the public attempts to access your website, they will do so by accessing a port of your public IP address, given by your router. Your router will need to forward the traffic to your computer. If you are using WSL, Windows will need to forward the traffic to WSL, since they have separate IP addresses. In order to make the website accessible by the public, you must complete (and debug) the following steps. 

2.1. Create firewall rules to allow traffic on port 55000. In powershell as an admin, run the following command to allow traffic through the firewall at the 55000 port. 

```{powershell admin}
New-NetFirewallRule -DisplayName "Allow PheWeb 55000" -Direction Inbound -LocalPort 55000 -Protocol TCP -Action Allow
```

2.2. Forward traffic from Windows to WSL2

```{powershell admin}
# get your WSL2 IP address
ip addr | grep eth0ep eth0 # inet 172.22.138.62/20 brd 172.22.143.255 scope global eth0

# forward traffic from Windows to WSL2
netsh interface portproxy add v4tov4 listenport=55000 listenaddress=0.0.0.0 connectport=55000 connectaddress=172.22.138.62
```

2.3. Create the Port forwarding Rule on Your Router.

In this step, you tell your router to forward traffic to your computer's IP address. First, go to your router's IP web address. This address can be found using the `ipconfig` command labelled under 'Default Gateway'. Once there, the process for creating the port forwarding rule varies by router. It can typically be completed by going to settings, NAT forwarding, or port forwarding, and creating a new rule. 

```{powershell}
# look for the IP address labelled 'Default Gateway'
ipconfig 
```


## Debugging Port Forwarding

1. Check that Pheweb is running locally at http://localhost:55000. If this step fails, then Pheweb is not running correctly. Check that you have set the correct port. 

2. Check that the website is available at the WSL2 windows address at http://<WSL2Address>:55000/. Check that the website is available at the Windows address http://<WindowsIPAddress>:55000/. If either of these step fails, then the firewall rules are not set correctly or Windows needs to forward traffic to WSL2.

3. Check that the website is available at the public IP address of your router http://<RouterAddress>:55000/. If this step fails, then port forwarding is not set up correctly.




## Docker Containers

Docker containers may be used to easily share Pheweb to an external server. 

1. Install Docker Desktop for Windows.

2. Enable WSL2 integration in Docker Desktop settings.

3. Create a new directory for the Dockerfile and copy over data from your pheweb deployment.

```{wsl}
mkdir pheweb_docker
cp -r ~/my-new-pheweb pheweb_docker
```

4. Create a Dockerfile and environment.yml file in the new directory. See the `docker_example` folder in this repository for an example.

5. Build the docker container

```{wsl}
cd pheweb_docker
docker build -t pheweb_docker .
```

6. Run the container. 

```{wsl}
docker run -p 55000:55000 pheweb_docker
```




## Developing PheWeb

1. Create and activate a new conda environment.

```
conda activate phewas_dev3
```

2. Fork the pheweb directory, then clone it to your machine. 

```
git clone https://github.com/<YourGithubUsername>/pheweb
```


3.  Install the local PheWeb repository in editable mode for development. 

```
cd pheweb
pip install --use-pep517 -e .
```


4. Test

```
pytest
```
