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


prepare-dev-env:
	pyenv virtualenv 3.10.7 dev
	pyenv local dev
	pyenv activate dev
	pip install -r requirements.txt
	pip install -e .
	cd terraform/dev/ && terraform apply -auto-approve && cd ../../ || cd ../../


download-msd-subset:
	python3 dev/flow/down.py

destroy-dev-env:
	cd terraform/ && terraform destroy -auto-approve && cd ../../ || cd ../../


run-dev-flow:
	python3 dev/flows/music_etl.py



prepare-prod-env:
	# terraform commands, pip install...

list-active-resources:
	# terraform output

run-etl:
	# Prefect / python command

install-aws-cli:
	mkdir -p tmp
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "tmp/awscliv2.zip"
	unzip -o tmp/awscliv2.zip -d tmp/ 
	sudo ./tmp/aws/install

install-terraform:
	wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	sudo apt update ; sudo apt install terraform

