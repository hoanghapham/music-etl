help:
	@echo "Available make commands:"

	@echo "      install-pyenv       : Shortcut to install pyenv"
	@echo "      setup-virtualenv    : Shortcut to setup a virtualenv"
	@echo "      setup-env           : Install required packages, and install current project as a local package"
	@echo "      download-msd-       : Shortcut to download the MSD subset"
	@echo "      extract-msd-dev     : Extract the MSD data in dev mode"
	@echo "      extract-msd-prod    : Extract the MSD data in prod mode (Go through all folders)"
	@echo "      run-etl-dev         : Run the ETL script in dev mode (Process only a few songs)"
	@echo "      run-etl-prod        : Run the ETL script in prod mode (Process all 1 million songs)"
	@echo "      install-aws-cli     : Short cut to install AWS CLI"
	@echo "      install-terraform   : Short cut to install Terraform"


install-pyenv:
	curl https://pyenv.run | bash
	sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev curl \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Dev
setup-virtualenv:
	pyenv virtualenv dev 
	pyenv local dev

setup-env:
	pip3 install -r etl/requirements.txt
	pip3 install -e etl/

download-msd-subset:
	python3 etl/flows/download_msd_subset.py

extract-msd-dev:
	python3 etl/flows/extract_msd_data.py -m dev

run-etl-dev:
	python3 etl/flows/music_etl.py -m dev

extract-msd-prod:
	python3 etl/flows/extract_msd_data.py -m prod

run-etl-prod:
	python3 etl/flows/music_etl.py -m prod

destroy-dev-infra:
	cd terraform/dev && terraform destroy -var-file secrets.tfvars -auto-approve && cd ../../	

install-aws-cli:
	mkdir -p tmp
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "tmp/awscliv2.zip"
	unzip -o tmp/awscliv2.zip -d tmp/ 
	sudo ./tmp/aws/install

install-terraform:
	wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	sudo apt update ; sudo apt install terraform

