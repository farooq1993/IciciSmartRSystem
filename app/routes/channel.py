from flask import Blueprint, request, jsonify, render_template, Response, redirect, url_for
from models.channel import CreateChannel, DataStructureField,DataStructureTemplate, FieldMapping
from utils.database import SessionLocal
from utils.extension import db
from datetime import datetime


channel = Blueprint("channel", __name__)
# db = SessionLocal()


@channel.route("/", methods=["GET"])
def get_channel_list():
    return jsonify({'msg':'all channels list'})


@channel.route('/create_channel', methods=['GET', 'POST'])
def create_channel():

        # If template_id passed → redirect to edit_template()
    template_id = request.args.get("template_id")
    if template_id:
        print("REDIRECTING TO TEMPLATE:", template_id)
        return redirect(url_for("channel.edit_template", template_id=template_id))

    if request.method == "POST":
        new_channel = CreateChannel(
            channel_name=request.form.get("channel_name"),
            channel_type=request.form.get("channel_type"),
            channel_source_path=request.form.get("channel_source_path"),
            channel_file_type=request.form.get("channel_file_type"),
            channel_username=request.form.get("channel_username"),
            channel_polling_freq=request.form.get("channel_polling_freq"),
            created_at=datetime.utcnow()
        )
        db.session.add(new_channel)
        db.session.commit()

        return redirect(url_for("channel.create_channel"))

    # GET METHOD:

    return render_template(
        "create_channel.html",
        channels=CreateChannel.query.all(),
        templates=DataStructureTemplate.query.all(),
        template=None
    )


@channel.route("/structure/template/add", methods=["POST"])
def add_template():
    tpl = DataStructureTemplate(
        name=request.form.get("name"),
        description=request.form.get("description")
    )
    db.session.add(tpl)
    db.session.commit()

    return redirect(url_for("channel.create_channel"))


# Add Field (AJAX)
@channel.route("/structure/template/<int:template_id>/field/add", methods=["POST"])
def add_field(template_id):
    max_sort = db.session.query(
        db.func.max(DataStructureField.sort_order)
    ).filter_by(template_id=template_id).scalar() or 0

    field = DataStructureField(
        template_id=template_id,
        field_name=request.form.get("field_name"),
        data_type=request.form.get("data_type"),
        format=request.form.get("format"),
        min_length=int(request.form.get("min_length")),
        max_length=int(request.form.get("max_length")),
        mandatory=("mandatory" in request.form),
        primary_key=("primary_key" in request.form),
        regex=request.form.get("regex"),
        sort_order=max_sort + 1,
    )

    db.session.add(field)
    db.session.commit()

    return {
        "id": field.id,
        "field_name": field.field_name,
        "data_type": field.data_type,
        "mandatory": field.mandatory,
        "primary_key": field.primary_key,
    }




# Select template
@channel.route("/structure/template/select")
def select_template():
    template_id = request.args.get("template_id")

    return redirect(url_for("channel.create_channel", template_id=template_id))

# @channel.route("/structure/template/select")
# def select_template():
#     template_id = request.args.get("template_id")
#     print("temi id", template_id)
#     if not template_id:
#         return redirect(url_for("channel.create_channel"))

#     return redirect(url_for("channel.edit_template", template_id=template_id))

@channel.route("/structure/template/<int:template_id>")
def edit_template(template_id):
    template = DataStructureTemplate.query.get_or_404(template_id)

    channels = CreateChannel.query.all()
    templates = DataStructureTemplate.query.all()

    # DEBUG: ensure fields and mappings load
    print("FIELDS:", [f.field_name for f in template.fields])
    print("MAPPINGS:", [(m.source_column, m.target_field) for m in template.mappings])

    return render_template(
        "create_channel.html",
        channels=channels,
        templates=templates,
        template=template
    )


@channel.route("/structure/field/<int:field_id>/edit", methods=["POST"])
def update_field(field_id):

    field = DataStructureField.query.get_or_404(field_id)
    form = request.form

    field.field_name = form.get("field_name")
    field.data_type = form.get("data_type")
    field.format = form.get("format")
    field.min_length = int(form.get("min_length"))
    field.max_length = int(form.get("max_length"))
    field.mandatory = ('mandatory' in form)
    field.primary_key = ('primary_key' in form)
    field.regex = form.get("regex")

    db.session.commit()

    return redirect(url_for("channel.edit_template", template_id=field.template_id))


@channel.route("/structure/field/<int:field_id>/delete", methods=["DELETE"])
def delete_field(field_id):
    f = DataStructureField.query.get_or_404(field_id)
    db.session.delete(f)
    db.session.commit()

    return {"success": True, "id": field_id}



#=====Route for Mapping=========

@channel.route("/structure/mapping/<int:template_id>/add", methods=["POST"])
def add_mapping(template_id):
    data = request.json

    mapping = FieldMapping(
        template_id=template_id,
        source_column=data["source_column"],
        target_field=data["target_field"],
        transformation=data.get("transformation")
    )
    db.session.add(mapping)
    db.session.commit()

    return {
        "id": mapping.id,
        "source_column": mapping.source_column,
        "target_field": mapping.target_field,
        "transformation": mapping.transformation,
    }, 200

@channel.route("/structure/mapping/<int:mapping_id>/update", methods=["PUT"])
def update_mapping(mapping_id):
    mapping = FieldMapping.query.get_or_404(mapping_id)
    data = request.json

    mapping.source_column = data["source_column"]
    mapping.target_field = data["target_field"]
    mapping.transformation = data.get("transformation")

    db.session.commit()
    return {"message": "updated"}, 200

@channel.route("/structure/mapping/<int:mapping_id>/delete", methods=["DELETE"])
def delete_mapping(mapping_id):
    mapping = FieldMapping.query.get_or_404(mapping_id)
    db.session.delete(mapping)
    db.session.commit()

    return {"message": "deleted"}, 200

