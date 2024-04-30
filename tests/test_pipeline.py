from compstrat import entrypoint, Args


def test_pipeline_with_mock_data():
    args = Args(
        strat1="ALPHA",
        strat2="BETA",
        run1="tests/resources/mock_runs/strat_alpha.csv",
        run2="tests/resources/mock_runs/strat_beta.csv",
        savedir="savedir",
    )
    entrypoint(args)
