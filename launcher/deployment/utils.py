import json
import os
from urlparse import urlparse
import redis
import requests
from django.conf import settings


def get_app_container_routing_data(deployment_instance, shipyard_response, deployment_domain):
    """Prepares data required to set up Hipache-Redis routing for an app.

    :param deployment_instance: Deployment model instance
    :param shipyard_response: dict representing the JSON payload received from Shipyard
    :param deployment_domain: e.g. demo.dev for local setup
    :return: (routing_data, app_urls) tuple, where `routing_data` can be used in HipacheRedisRouter.add_routes() call
        and `app_urls` are the actual URLs that can be used to launch the deployed app in the browser
    """
    docker_server = urlparse(shipyard_response[0]['engine']['addr'])
    docker_server_ip = docker_server.hostname

    # maps internal container ports to public ports (for example: 80 -> 49302)
    public_container_port_mapping = {port["container_port"]: port["port"] for port in shipyard_response[0]["ports"]}

    domain_to_public_port_mapping = []
    hostname_list = deployment_instance.project.hostname_list
    if hostname_list:
        for i, hostname in enumerate(hostname_list):
            domain = "{0}-{1}.{2}".format(hostname, deployment_instance.deploy_id, deployment_domain)
            domain_to_public_port_mapping.append(
                (domain, public_container_port_mapping[deployment_instance.project.port_list[i]]))
    else:
        domain = "{0}.{1}".format(deployment_instance.deploy_id, deployment_domain)
        domain_to_public_port_mapping.append(
            (domain, public_container_port_mapping[deployment_instance.project.port_list[0]]))

    routing_data = []
    app_urls = []
    for domain, public_port in domain_to_public_port_mapping:
        key = 'frontend:{0}'.format(domain)
        routing_data.append([key, deployment_instance.deploy_id, "{0}://{1}:{2}".format(
            deployment_instance.project.scheme, docker_server_ip, public_port)])
        app_urls.append("{0}://{1}".format(deployment_instance.project.scheme, domain))

    return routing_data, app_urls


def get_status_page_routing_data(deployment_instance, deployment_domain):
    """Prepares data required to set up Hipache-Redis/nginx redirection to the app's status page.

    :param deployment_instance: Deployment model instance
    :param deployment_domain: e.g. demo.dev for local setup
    :return: Routing data which can be used in HipacheRedisRouter.add_routes() call
    """
    hostname_list = deployment_instance.project.hostname_list
    domains = []
    if hostname_list:
        for i, hostname in enumerate(hostname_list):
            domain = "{0}-{1}.{2}".format(hostname, deployment_instance.deploy_id, deployment_domain)
            domains.append(domain)
    else:
        domain = "{0}.{1}".format(deployment_instance.deploy_id, deployment_domain)
        domains.append(domain)

    routing_data = []
    for domain in domains:
        key = 'frontend:{0}'.format(domain)
        # TODO: Both IP & port should be passed here from the outside!
        #       `:8002` should match nginx.conf
        routing_data.append([key, deployment_instance.deploy_id, "{0}://{1}:8002".format(
            deployment_instance.project.scheme, os.environ['LAUNCHER_IP'])])

    return routing_data


class HipacheRedisRouter(object):
    def __init__(self, host=settings.HIPACHE_REDIS_IP, port=settings.HIPACHE_REDIS_PORT, db=0):
        self.redis_instance = redis.StrictRedis(host=host, port=port, db=db)
        # https://github.com/andymccurdy/redis-py#pipelines
        self.pipe = self.redis_instance.pipeline()

    def add_routes(self, routing_data):
        for key, route_id, route_url in routing_data:
            self.pipe.delete(key).rpush(key, route_id, route_url)

    def commit(self):
        self.pipe.execute()


class ShipyardWrapper(object):
    def __init__(self, shipyard_host=settings.SHIPYARD_HOST, shipyard_key=settings.SHIPYARD_KEY):
        self.shipyard_host = shipyard_host
        self.shipyard_key = shipyard_key

    def deploy(self, payload):
        headers = {'X-Service-Key': self.shipyard_key,
                   'content-type': 'application/json'}
        response = requests.post("{0}/api/containers".format(self.shipyard_host),
                                 data=json.dumps(payload),
                                 headers=headers)
        return response

    def _get_request(self, action, container_id):
        headers = {'X-Service-Key': self.shipyard_key}
        response = requests.get("{0}/api/containers/{1}{2}".format(self.shipyard_host, container_id, action),
                                headers=headers)
        return response

    def restart(self, container_id):
        return self._get_request(action='/restart', container_id=container_id)

    def stop(self, container_id):
        return self._get_request(action='/stop', container_id=container_id)

    def inspect(self, container_id):
        return self._get_request('', container_id=container_id)
