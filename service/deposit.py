import sword2
from octopus.modules.swordv2 import client_http
from octopus.core import app

def deposit(payload_path, username, password, collection, on_behalf_of=None, mimetype="application/zip",
            packaging="http://purl.org/net/sword/package/METSDSpaceSIP"):
    conn = sword2.Connection(user_name=username, user_pass=password, error_response_raises_exceptions=True,
                             http_impl=client_http.OctopusHttpLayer(timeout=app.config.get("DEPOSIT_TIMEOUT")))
    with open(payload_path) as f:
        receipt = conn.create(col_iri=collection, payload=f, mimetype=mimetype, filename=f.name.split("/")[-1],
                              packaging=packaging, on_behalf_of=on_behalf_of)

    if receipt is None:
        return None
    elif isinstance(receipt, sword2.Error_Document):
        raise sword2.ServerError(None, receipt.to_xml())
    else:
        return receipt.edit


def poll(edit_iri, username, password):
    conn = sword2.Connection(user_name=username, user_pass=password, error_response_raises_exceptions=True,
                             http_impl=client_http.OctopusHttpLayer())

    try:
        receipt = conn.get_deposit_receipt(edit_iri)
    except sword2.HTTPResponseError as e:
        if e.response.status == 404:
            return None, None
        raise

    if receipt is None:
        return None, None
    if receipt.code == 404:
        return None, None

    atom = receipt.atom_statement_iri
    ore = receipt.ore_statement_iri

    statement = None
    if atom is not None:
        statement = conn.get_atom_sword_statement(atom)
    if statement is None and ore is not None:
        statement = conn.get_ore_sword_statement(ore)
    return receipt, statement

def get_file(file_iri, username, password):
    conn = sword2.Connection(user_name=username, user_pass=password, error_response_raises_exceptions=False,
                             http_impl=client_http.OctopusHttpLayer())
    return conn.get_resource(content_iri = file_iri)