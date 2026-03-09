from app.utils.temperature_models import ratkowsky_mu_max


def test_ratkowsky_mu_max_zero_below_tmin():
    assert ratkowsky_mu_max(-2.0, 0.02, -1.5) == 0.0


def test_ratkowsky_mu_max_increases_with_temperature():
    cold = ratkowsky_mu_max(4.0, 0.02, -1.5)
    warm = ratkowsky_mu_max(12.0, 0.02, -1.5)
    assert warm > cold > 0.0
