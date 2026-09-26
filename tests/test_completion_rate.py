def test_half_done(service):
    a = service.create_task("a")
    service.create_task("b")
    service.complete_task(a.id)
    assert service.completion_rate() == 50.0


def test_rounds_to_one_decimal(service):
    a = service.create_task("a")
    service.create_task("b")
    service.create_task("c")
    service.complete_task(a.id)
    assert service.completion_rate() == 33.3
