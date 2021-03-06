import io
import os
import pytest
import numpy as np
import nbformat
from temp_utils import _get_hdf5_params
from libertem.web.notebook_generator.notebook_generator import notebook_generator
from nbconvert.preprocessors import ExecutePreprocessor


@pytest.mark.skip(reason="requires `empyre`")
def test_com_default(hdf5_ds_2, tmpdir_factory, lt_ctx):
    datadir = tmpdir_factory.mktemp('template_tests')

    conn = {'connection': {'type': 'local'}}
    path = hdf5_ds_2.path
    dataset = _get_hdf5_params(path)

    analysis = [{
            "analysisType": 'CENTER_OF_MASS',
            "parameters": {
                        'shape': 'com',
                        'cx': 0,
                        'cy': 0,
                        'r': 8,
                        }
    }]

    notebook = notebook_generator(conn, dataset, analysis, save=True)
    notebook = io.StringIO(notebook.getvalue())
    nb = nbformat.read(notebook, as_version=4)
    ep = ExecutePreprocessor(timeout=600)
    out = ep.preprocess(nb, {"metadata": {"path": datadir}})
    channels = [
            "field",
            "magnitude",
            "divergence",
            "curl",
            "x",
            "y"
    ]
    results = {}
    for channel in channels:
        data_path = os.path.join(datadir, f"com_result_{channel}.npy")
        results[channel] = np.load(data_path)

    com_analysis = lt_ctx.create_com_analysis(
                                dataset=hdf5_ds_2,
                                cx=0,
                                cy=0,
                                mask_radius=8
                            )
    expected = lt_ctx.run(com_analysis)

    assert np.allclose(results["field"], expected["field"].raw_data)
    assert np.allclose(results["magnitude"], expected["magnitude"].raw_data)
    assert np.allclose(results["divergence"], expected["divergence"].raw_data)
    assert np.allclose(results["curl"], expected["curl"].raw_data)
    assert np.allclose(results["x"], expected["x"].raw_data)
    assert np.allclose(results["y"], expected["y"].raw_data)
