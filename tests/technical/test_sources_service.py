import pytest
from sakia.data.entities import Transaction
from sakia.data.processors import TransactionsProcessor


@pytest.mark.asyncio
async def test_receive_source(application_with_one_connection, fake_server, bob, alice):
    amount = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    fake_server.forge.push(alice.send_money(150, fake_server.forge.user_identities[alice.key.pubkey].sources, bob,
                                            fake_server.forge.blocks[-1].blockUID, "Test receive"))
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    new_blocks = fake_server.forge.blocks[-3:]
    changed_tx, new_tx, new_ud = await application_with_one_connection.transactions_service.handle_new_blocks(new_blocks)
    await application_with_one_connection.sources_service.refresh_sources(new_tx, new_ud)
    assert amount + 150 == application_with_one_connection.sources_service.amount(bob.key.pubkey)
    await fake_server.close()


@pytest.mark.asyncio
async def test_send_source(application_with_one_connection, fake_server, bob, alice):
    amount = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    fake_server.forge.push(bob.send_money(150, fake_server.forge.user_identities[bob.key.pubkey].sources, alice,
                                            fake_server.forge.blocks[-1].blockUID, "Test receive"))
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    new_blocks = fake_server.forge.blocks[-3:]
    changed_tx, new_tx, new_ud = await application_with_one_connection.transactions_service.handle_new_blocks(new_blocks)
    await application_with_one_connection.sources_service.refresh_sources(new_tx, new_ud)
    assert amount - 150 == application_with_one_connection.sources_service.amount(bob.key.pubkey)
    await fake_server.close()


@pytest.mark.asyncio
async def test_destruction(application_with_one_connection, fake_server, bob, alice):
    amount = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    fake_server.forge.push(bob.send_money(amount - 80, fake_server.forge.user_identities[bob.key.pubkey].sources, alice,
                                            fake_server.forge.blocks[-1].blockUID, "Test receive"))
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    fake_server.forge.forge_block()
    new_blocks = fake_server.forge.blocks[-3:]
    changed_tx, new_tx, new_ud = await application_with_one_connection.transactions_service.handle_new_blocks(new_blocks)
    await application_with_one_connection.sources_service.refresh_sources(new_tx, new_ud)
    assert 0 == application_with_one_connection.sources_service.amount(bob.key.pubkey)
    tx_after_parse = application_with_one_connection.transactions_service.transfers(bob.key.pubkey)
    assert tx_after_parse[-1].comment == "Too low balance"
    await fake_server.close()


@pytest.mark.asyncio
async def test_send_tx_then_cancel(application_with_one_connection, fake_server, bob, alice):
    tx_before_send = application_with_one_connection.transactions_service.transfers(bob.key.pubkey)
    sources_before_send = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    bob_connection = application_with_one_connection.db.connections_repo.get_one(pubkey=bob.key.pubkey)
    fake_server.reject_next_post = True
    await application_with_one_connection.documents_service.send_money(bob_connection,
                                                                       bob.salt,
                                                                       bob.password,
                                                                       alice.key.pubkey, 10, 0, "Test comment")
    tx_after_send = application_with_one_connection.transactions_service.transfers(bob.key.pubkey)
    sources_after_send = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    assert len(tx_before_send) + 1 == len(tx_after_send)
    assert sources_before_send - 10 >= sources_after_send
    assert tx_after_send[-1].state is Transaction.REFUSED
    assert tx_after_send[-1].written_block == 0

    transactions_processor = TransactionsProcessor.instanciate(application_with_one_connection)
    if transactions_processor.cancel(tx_after_send[-1]):
        application_with_one_connection.sources_service.restore_sources(bob.key.pubkey, tx_after_send[-1])

    tx_after_cancel = application_with_one_connection.transactions_service.transfers(bob.key.pubkey)
    sources_after_cancel = application_with_one_connection.sources_service.amount(bob.key.pubkey)
    assert tx_after_cancel[-1].state is Transaction.DROPPED
    assert tx_after_cancel[-1].written_block == 0
    assert len(tx_before_send) + 1 == len(tx_after_cancel)
    assert sources_before_send == sources_after_cancel

    await fake_server.close()