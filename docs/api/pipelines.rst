pyodas2.pipelines
##################

Classes
********

.. autoclass:: pyodas2.pipelines.SslPipeline

   .. automethod:: __init__
   .. automethod:: process

.. autoclass:: pyodas2.pipelines.SslPipelineResult
   :special-members: __init__
   :members:
   :undoc-members:

|

.. autoclass:: pyodas2.pipelines.SstPipeline

   .. automethod:: __init__
   .. automethod:: process

.. autoclass:: pyodas2.pipelines.SstPipelineResult
   :special-members: __init__
   :members:
   :undoc-members:

|

.. autoclass:: pyodas2.pipelines.DelaySumPipeline

   .. automethod:: __init__
   .. automethod:: process

.. autoclass:: pyodas2.pipelines.DelaySumPipelineResult
   :special-members: __init__
   :members:
   :undoc-members:

|

.. autoclass:: pyodas2.pipelines.SteeringDelaySumPipeline

   .. automethod:: __init__
   .. automethod:: process

.. autoclass:: pyodas2.pipelines.SteeringDelaySumPipelineResult
   :special-members: __init__
   :members:
   :undoc-members:

|

.. autoclass:: pyodas2.pipelines.SstDelaySumPipeline

   .. automethod:: __init__
   .. automethod:: process

.. autoclass:: pyodas2.pipelines.SstDelaySumPipelineResult
   :special-members: __init__
   :members:
   :undoc-members:

|

.. autoclass:: pyodas2.pipelines.AcousticImageCalibrationPipeline

   .. automethod:: __init__
   .. autoproperty:: targets
   .. autoproperty:: current_target_index
   .. autoproperty:: is_finished
   .. automethod:: process
   .. automethod:: record_tdoas
   .. automethod:: calibrate

|

.. autoclass:: pyodas2.pipelines.AcousticImagePipeline

   .. automethod:: __init__
   .. automethod:: process
   .. automethod:: generate_acoustic_image
