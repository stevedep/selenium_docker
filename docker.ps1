# Variables
$acr_id = "stevedep.azurecr.io"
# Create docker image using docker desktop
docker login $acr_id -u StevedeP -p W17@b83!!
docker build --tag $acr_id/selenium .
# Push docker image to Azure Container Registry
docker push $acr_id/selenium:latest