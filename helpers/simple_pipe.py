from bob.bio.base.pipelines.vanilla_biometrics import Distance, VanillaBiometricsPipeline
from sklearn.pipeline import make_pipeline
from bob.bio.face.utils import cropped_positions_arcface, dnn_default_cropping, make_cropper
from bob.pipelines import wrap
from bob.bio.face.utils import lookup_config_from_database
from bob.bio.face.embeddings.mxnet import ArcFaceInsightFace_LResNet100
from sklearn.base import TransformerMixin, BaseEstimator


class simple(TransformerMixin, BaseEstimator):  # Define a sample transformer
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fit(self, X, y=None):  # fit function
        return self

    def transform(self, X):  # compute rank list
        return X


def embedding_transformer(
        cropped_image_size,
        embedding,
        cropped_positions,
        fixed_positions=None,
        color_channel="rgb",
        annotator=None,
        **kwargs
):
    """
    Creates a pipeline composed by and FaceCropper and an Embedding extractor.
    This transformer is suited for Facenet based architectures

    .. warning::
       This will resize images to the requested `image_size`

    """
    face_cropper, transform_extra_arguments = make_cropper(
        cropped_image_size=cropped_image_size,
        cropped_positions=cropped_positions,
        fixed_positions=fixed_positions,
        color_channel=color_channel,
        annotator=annotator,
        **kwargs
    )
    # breakpoint()
    trans = simple()
    transformer = make_pipeline(
        wrap(
            ["sample"],
            face_cropper,
            transform_extra_arguments=transform_extra_arguments,
        ),
        wrap(["sample"], embedding),
        wrap(["sample"], trans)  # Add simple transformer
    )

    return transformer


def arcface_template(embedding, annotation_type, fixed_positions=None):
    # DEFINE CROPPING
    cropped_image_size = (112, 112)

    if annotation_type == "eyes-center" or annotation_type == "bounding-box":
        # Hard coding eye positions for backward consistency
        # cropped_positions = {
        cropped_positions = cropped_positions_arcface()
        if annotation_type == "bounding-box":
            # This will allow us to use `BoundingBoxAnnotatorCrop`
            cropped_positions.update(
                {"topleft": (0, 0), "bottomright": cropped_image_size}
            )

    elif isinstance(annotation_type, list):
        cropped_positions = cropped_positions_arcface(annotation_type)
    else:
        cropped_positions = dnn_default_cropping(cropped_image_size, annotation_type)

    annotator = None
    transformer = embedding_transformer(
        cropped_image_size=cropped_image_size,
        embedding=embedding,
        cropped_positions=cropped_positions,
        fixed_positions=fixed_positions,
        color_channel="rgb",
        annotator=annotator,
    )

    algorithm = Distance()

    return VanillaBiometricsPipeline(transformer, algorithm)


def arcface_insightFace_lresnet100(
        annotation_type, fixed_positions=None, memory_demanding=False
):
    return arcface_template(
        ArcFaceInsightFace_LResNet100(memory_demanding=memory_demanding),
        annotation_type,
        fixed_positions,
    )


# pipeline
annotation_type, fixed_positions, memory_demanding = lookup_config_from_database(
    locals().get("database")
)


def load(annotation_type, fixed_positions=None):
    return arcface_insightFace_lresnet100(
        annotation_type=annotation_type,
        fixed_positions=fixed_positions,
        memory_demanding=memory_demanding,
    )


pipeline = load(annotation_type, fixed_positions)
transformer = pipeline.transformer
