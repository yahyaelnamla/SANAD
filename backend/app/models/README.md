# SANAD/backend/app/models/

This directory contains the database models for the SANAD backend application. These models define the structure of the data stored in the PostgreSQL database and are typically implemented using an Object-Relational Mapper (ORM) like SQLAlchemy.

## Purpose:
To provide a clear and consistent representation of the application's data entities, facilitating interaction with the database and ensuring data integrity. These models are used for creating, reading, updating, and deleting records in the database.

## Contents:
- `user.py`: Defines the User model.
- `session.py`: Defines the Session model for user sessions.
- `query.py`: Defines the Query model for user queries.
- `source.py`: Defines the Source model for knowledge sources.
- `citation.py`: Defines the Citation model for references.
- `fatwa.py`: Defines the Fatwa model for jurisprudential rulings.
- `scholar.py`: Defines the Scholar model.
- `fiqh_rule.py`: Defines the FiqhRule model.
- `company.py`: Defines the Company model for Shariah compliance screening.
- `crypto_asset.py`: Defines the CryptoAsset model.

## Limitations:
- Models should primarily focus on data definition and relationships. Business logic should be delegated to the `services/` or `repositories/` layers.
- Avoid complex queries directly within the model definitions; use repositories for query abstraction.

## Needs:
- Accurate mapping to the `DATABASE_SCHEMA.md`.
- Proper definition of relationships between models.
- Validation rules for data integrity.

## Usage for AI Agents:
AI agents working on the backend should implement these models based on the `DATABASE_SCHEMA.md`. They must ensure that the models accurately reflect the database structure and include necessary validations and relationships. Testing of model interactions with the database is crucial.
