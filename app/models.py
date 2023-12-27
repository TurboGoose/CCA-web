import os

from flask_sqlalchemy import SQLAlchemy

from config import DATABASE_FILE

db = SQLAlchemy()


class Dataset(db.Model):
    __tablename__ = "datasets"
    name = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    labels = db.relationship(
        "Label", back_populates="dataset", cascade="all, delete", passive_deletes=True
    )


class Label(db.Model):
    __tablename__ = "labels"
    dataset_name = db.Column(
        db.String,
        db.ForeignKey("datasets.name", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    name = db.Column(db.String, primary_key=True, nullable=False)
    dataset = db.relationship("Dataset", back_populates="labels")


def init_db():
    if not os.path.exists(DATABASE_FILE):
        open(DATABASE_FILE, "w").close()

    db.session.commit()
    db.drop_all()
    db.create_all()
    db.session.commit()


def save_dataset(dataset_name):
    new_dataset = Dataset(name=dataset_name)
    db.session.add(new_dataset)
    db.session.commit()


def get_datasets():
    return [dataset.name for dataset in db.session.query(Dataset).all()]


def rename_dataset(old_dataset_name, new_dataset_name):
    db.session.execute(
        db.update(Dataset)
        .where(Dataset.name == old_dataset_name)
        .values(name=new_dataset_name)
    )
    db.session.commit()


def delete_dataset(dataset_name):
    dataset_to_delete = db.session.query(Dataset).get(dataset_name)
    db.session.delete(dataset_to_delete)
    db.session.commit()


def save_label_for_dataset(label_name, dataset_name):
    new_label = Label(dataset_name=dataset_name, name=label_name)
    db.session.add(new_label)
    db.session.commit()


def get_labels_for_dataset(dataset_name):
    return [
        label.name
        for label in db.session.query(Label).filter_by(dataset_name=dataset_name).all()
    ]


def rename_label_for_dataset(dataset_name, old_label_name, new_label_name):
    label_to_rename = db.session.query(Label).get((dataset_name, old_label_name))
    label_to_rename.name = new_label_name
    db.session.commit()


def delete_label_for_dataset(label_name, dataset_name):
    label_to_delete = db.session.query(Label).get((dataset_name, label_name))
    db.session.delete(label_to_delete)
    db.session.commit()
