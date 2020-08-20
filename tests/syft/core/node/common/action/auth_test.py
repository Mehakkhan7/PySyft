import pytest
from nacl.signing import SigningKey
from nacl.signing import VerifyKey

import syft as sy

from syft.core.node.common.action.auth import service_auth


def test_service_auth_root_fails() -> None:
    node = sy.Device()
    msg = sy.ReprMessage(address=node.address)

    random_signing_key = SigningKey.generate()
    random_verify_key = random_signing_key.verify_key

    # root_only
    @service_auth(root_only=True)
    def process(node: sy.Device, msg: sy.ReprMessage, verify_key: VerifyKey) -> None:
        pass

    process(node=node, msg=msg, verify_key=node.root_verify_key)

    with pytest.raises(Exception, match="User is not root."):
        process(node=node, msg=msg, verify_key=random_verify_key)


def test_service_auth_existing_user() -> None:
    node = sy.Device()
    msg = sy.ReprMessage(address=node.address)
    random_signing_key = SigningKey.generate()
    random_verify_key = random_signing_key.verify_key

    # existing_users_only
    @service_auth(existing_users_only=True)
    def process(node: sy.Device, msg: sy.ReprMessage, verify_key: VerifyKey) -> None:
        pass

    with pytest.raises(Exception, match="User not known."):
        process(node=node, msg=msg, verify_key=random_verify_key)

    # NOTE didn't find a method to add a key to guest_verify_key_registry
    node.guest_verify_key_registry.add(random_verify_key)
    process(node=node, msg=msg, verify_key=random_verify_key)


def test_service_auth_guests_fails() -> None:
    node = sy.Device()
    msg = sy.ReprMessage(address=node.address)
    new_signing_key = SigningKey.generate()
    new_verify_key = new_signing_key.verify_key

    # guests_welcome
    @service_auth(guests_welcome=True)
    def process(node: sy.Device, msg: sy.ReprMessage, verify_key: VerifyKey) -> None:
        pass

    process(node=node, msg=msg, verify_key=new_verify_key)

    assert new_verify_key not in node.guest_verify_key_registry


def test_service_auth_guests_succeeds() -> None:
    node = sy.Device()
    msg = sy.ReprMessage(address=node.address)
    new_signing_key = SigningKey.generate()
    new_verify_key = new_signing_key.verify_key

    # register_new_guests
    @service_auth(guests_welcome=True, register_new_guests=True)
    def process(node: sy.Device, msg: sy.ReprMessage, verify_key: VerifyKey) -> None:
        pass

    process(node=node, msg=msg, verify_key=new_verify_key)

    assert new_verify_key in node.guest_verify_key_registry
