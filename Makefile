help:
	@echo "Available make commands:"
	@echo "  Command: desc"
	@echo "  Command: desc"
	@echo "  Command: desc"
	@echo "  Command: desc"
	@echo "  Command: desc"
	@echo "  Command: desc"
	@echo "  Command: desc"

install-pyenv:
	curl https://pyenv.run | bash
	pyenv install -f 3.10.7


setup-dev-infra:
	cd terraform/dev/ && terraform apply -var-file="secrets.tfvars" -auto-approve && cd ../../ || cd ../../


setup-virtualenv:
	pyenv virtualenv -f 3.10.7 dev 
	pyenv local dev

setup-dev-env:
	pip install -r etl/requirements.txt
	pip install -e etl/

download-msd-subset:
	python3 etl/flows/download_msd_subset.py

extract-msd-data:
	python3 etl/flows/extract_msd_data.py

run-etl:
	python3 etl/flows/music_etl.py

destroy-dev-env:
	cd terraform/ && terraform destroy -auto-approve && cd ../../ || cd ../../

prepare-prod-env:
	# terraform commands, pip install...

list-active-resources:
	# terraform output

install-aws-cli:
	mkdir -p tmp
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "tmp/awscliv2.zip"
	unzip -o tmp/awscliv2.zip -d tmp/ 
	sudo ./tmp/aws/install

install-terraform:
	wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	sudo apt update ; sudo apt install terraform

