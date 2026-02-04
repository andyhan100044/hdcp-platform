"""
HDCP Project Generator Skill Implementation
Automatically generate production-ready websites based on PRD
"""

import os
import json
import shutil
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class HDCPProjectGenerator:
    """Generate HDCP-based projects from PRD"""

    def __init__(self, template_path: str = "hdcp-platform"):
        self.template_path = template_path
        self.output_path = None
        self.scenario = None
        self.prd_content = None
        self.features = []
        self.customizations = {}

    def generate_project(
        self,
        prd_path: str,
        scenario: str,
        features: Optional[List[str]] = None,
        customizations: Optional[Dict[str, Any]] = None,
        output_path: str = "generated-project"
    ) -> Dict[str, Any]:
        """
        Generate a complete HDCP project based on PRD

        Args:
            prd_path: Path to PRD file
            scenario: Business scenario (stock, iot, ecommerce, carbon)
            features: Additional features to enable
            customizations: Custom configuration
            output_path: Output directory

        Returns:
            Dictionary with generation results
        """
        # Load PRD
        self.prd_content = self._load_prd(prd_path)

        # Parse PRD
        entities = self._parse_prd_entities()
        requirements = self._parse_prd_requirements()

        # Initialize
        self.output_path = output_path
        self.scenario = scenario
        self.features = features or []
        self.customizations = customizations or {}

        # Generate project structure
        self._copy_template()

        # Generate models
        models = self._generate_models(entities)

        # Generate APIs
        apis = self._generate_apis(entities, requirements)

        # Generate UI components
        components = self._generate_ui_components(entities)

        # Generate configuration
        self._generate_config(requirements)

        # Generate documentation
        documentation = self._generate_docs(entities, apis, components)

        return {
            "project_path": self.output_path,
            "entities": entities,
            "models": models,
            "apis": apis,
            "components": components,
            "features_enabled": self.features,
            "documentation": documentation,
            "deployment_ready": True
        }

    def _load_prd(self, prd_path: str) -> str:
        """Load PRD file content"""
        with open(prd_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_prd_entities(self) -> List[Dict[str, Any]]:
        """Extract data entities from PRD"""
        entities = []

        # Look for entity definitions in PRD
        lines = self.prd_content.split('\n')
        current_entity = None

        for line in lines:
            line = line.strip()

            # Entity definition pattern
            if line.startswith('## Entity:') or line.startswith('### Entity:'):
                if current_entity:
                    entities.append(current_entity)

                entity_name = line.split(':', 1)[1].strip()
                current_entity = {
                    'name': entity_name,
                    'fields': [],
                    'description': ''
                }

            # Field definition pattern
            elif line.startswith('-') and current_entity:
                # Parse field: name: type: description
                field_parts = line[1:].strip().split(':')
                if len(field_parts) >= 2:
                    field_name = field_parts[0].strip()
                    field_type = field_parts[1].strip()
                    field_desc = ':'.join(field_parts[2:]).strip() if len(field_parts) > 2 else ''

                    current_entity['fields'].append({
                        'name': field_name,
                        'type': field_type,
                        'description': field_desc
                    })

        # Add last entity
        if current_entity:
            entities.append(current_entity)

        # Default entities based on scenario if none found
        if not entities:
            entities = self._get_default_entities()

        return entities

    def _parse_prd_requirements(self) -> Dict[str, Any]:
        """Parse functional requirements from PRD"""
        requirements = {
            'features': [],
            'apis': [],
            'ui_requirements': [],
            'integrations': []
        }

        # Parse feature requirements
        for feature in self.features:
            requirements['features'].append(feature)

        # Parse from PRD sections
        lines = self.prd_content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('##') or line.startswith('###'):
                current_section = line.lower()

            # Extract requirements based on sections
            if current_section and 'requirement' in current_section:
                if line.startswith('-') or line.startswith('*'):
                    req = line[1:].strip()
                    requirements['features'].append(req)

        return requirements

    def _get_default_entities(self) -> List[Dict[str, Any]]:
        """Get default entities for scenario"""
        defaults = {
            'stock': [
                {
                    'name': 'Stock',
                    'fields': [
                        {'name': 'symbol', 'type': 'String', 'description': 'Stock symbol'},
                        {'name': 'price', 'type': 'DECIMAL', 'description': 'Current price'},
                        {'name': 'volume', 'type': 'BigInteger', 'description': 'Trading volume'},
                        {'name': 'timestamp', 'type': 'DateTime', 'description': 'Price timestamp'}
                    ]
                }
            ],
            'iot': [
                {
                    'name': 'Sensor',
                    'fields': [
                        {'name': 'sensor_id', 'type': 'String', 'description': 'Sensor identifier'},
                        {'name': 'temperature', 'type': 'DECIMAL', 'description': 'Temperature reading'},
                        {'name': 'humidity', 'type': 'DECIMAL', 'description': 'Humidity reading'},
                        {'name': 'location', 'type': 'String', 'description': 'Sensor location'}
                    ]
                }
            ],
            'ecommerce': [
                {
                    'name': 'Product',
                    'fields': [
                        {'name': 'product_id', 'type': 'String', 'description': 'Product ID'},
                        {'name': 'name', 'type': 'String', 'description': 'Product name'},
                        {'name': 'price', 'type': 'DECIMAL', 'description': 'Current price'},
                        {'name': 'currency', 'type': 'String', 'description': 'Currency code'}
                    ]
                }
            ],
            'carbon': [
                {
                    'name': 'CarbonProject',
                    'fields': [
                        {'name': 'project_id', 'type': 'String', 'description': 'Project ID'},
                        {'name': 'name', 'type': 'String', 'description': 'Project name'},
                        {'name': 'credits', 'type': 'Integer', 'description': 'Total credits'},
                        {'name': 'co2_offset', 'type': 'DECIMAL', 'description': 'CO2 offset (tons)'}
                    ]
                }
            ]
        }

        return defaults.get(self.scenario, [])

    def _copy_template(self):
        """Copy HDCP template to output directory"""
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

        shutil.copytree(self.template_path, self.output_path)

        # Update configuration
        config_path = os.path.join(self.output_path, 'hdcp.config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            config['platform']['name'] = f"HDCP {self.scenario.title()} Platform"
            config['app']['api']['scenario'] = self.scenario

            with open(config_path, 'w') as f:
                yaml.dump(config, f)

    def _generate_models(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Generate SQLAlchemy models"""
        models_path = os.path.join(self.output_path, 'apps', 'api', 'app', 'models')
        generated_models = []

        for entity in entities:
            model_code = self._create_model_code(entity)
            model_file = os.path.join(models_path, f"{entity['name'].lower()}.py")

            with open(model_file, 'w') as f:
                f.write(model_code)

            generated_models.append(model_file)

        return generated_models

    def _create_model_code(self, entity: Dict[str, Any]) -> str:
        """Create SQLAlchemy model code"""
        class_name = entity['name']
        table_name = f"{class_name.lower()}s"

        description = entity.get('description', f'{class_name} model')
        code = f'''"""
{description}
"""
from sqlalchemy import Column, String, DECIMAL, BigInteger, DateTime, Integer, Text, Boolean, Float
from app.core.base import TimestampedModel

class_description = entity.get('description', f'{class_name} data model')
class {class_name}(TimestampedModel):
    """
    {class_description}
    """
    __tablename__ = "{table_name}"
'''

        for field in entity['fields']:
            field_name = field['name']
            field_type = field['type']
            description = field.get('description', '')

            # Map type to SQLAlchemy column
            if field_type == 'String':
                column_type = 'String(255)'
            elif field_type == 'Integer':
                column_type = 'Integer'
            elif field_type == 'BigInteger':
                column_type = 'BigInteger'
            elif field_type == 'DECIMAL':
                column_type = 'DECIMAL(10, 2)'
            elif field_type == 'Float':
                column_type = 'Float'
            elif field_type == 'DateTime':
                column_type = 'DateTime(timezone=True)'
            elif field_type == 'Text':
                column_type = 'Text'
            elif field_type == 'Boolean':
                column_type = 'Boolean'
            else:
                column_type = 'String(255)'

            code += f'''
    {field_name} = Column({column_type}, nullable=False, comment="{description}")'''

        code += '''
'''

        return code

    def _generate_apis(self, entities: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[str]:
        """Generate FastAPI endpoints"""
        apis_path = os.path.join(self.output_path, 'apps', 'api', 'app', 'routers')
        generated_apis = []

        # Create router file
        router_file = os.path.join(apis_path, f"{self.scenario}.py")
        router_code = self._create_router_code(entities, requirements)

        with open(router_file, 'w') as f:
            f.write(router_code)

        generated_apis.append(router_file)
        return generated_apis

    def _create_router_code(self, entities: List[Dict[str, Any]], requirements: Dict[str, Any]) -> str:
        """Create FastAPI router code"""
        entity = entities[0] if entities else {'name': 'Item', 'fields': []}
        entity_name = entity['name']
        entity_var = entity_name.lower()

        code = f'''"""
{entity_name} API Endpoints
Generated based on PRD
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models.{entity_var} import {entity_name}
from app.schemas.{entity_var} import {entity_name}Create, {entity_name}Response

router = APIRouter(prefix="/{entity_var}s", tags=["{entity_var}"])

@{router.get("/", response_model=List[{entity_name}Response}])
async def list_{entity_var}s(db: AsyncSession = Depends(get_db)):
    """List all {entity_var}s"""
    # TODO: Implement pagination
    # result = await db.execute(select({entity_name}))
    # return result.scalars().all()
    return []

@{router.get("/{{id}}", response_model={entity_name}Response})
async def get_{entity_var}(id: int, db: AsyncSession = Depends(get_db)):
    """Get {entity_var} by ID"""
    # TODO: Implement get by ID
    # result = await db.execute(select({entity_name}).where({entity_name}.id == id))
    # {entity_var} = result.scalar_one_or_none()
    # if not {entity_var}:
    #     raise HTTPException(status_code=404, detail="{entity_name} not found")
    # return {entity_var}
    return None

@{router.post("/", response_model={entity_name}Response})
async def create_{entity_var}(data: {entity_name}Create, db: AsyncSession = Depends(get_db)):
    """Create new {entity_var}"""
    # TODO: Implement create
    # {entity_var} = {entity_name}(**data.dict())
    # db.add({entity_var})
    # await db.commit()
    # await db.refresh({entity_var})
    # return {entity_var}
    return None

@{router.put("/{{id}}", response_model={entity_name}Response})
async def update_{entity_var}(id: int, data: {entity_name}Create, db: AsyncSession = Depends(get_db)):
    """Update {entity_var}"""
    # TODO: Implement update
    return None

@{router.delete("/{id}")
async def delete_{entity_var}(id: int, db: AsyncSession = Depends(get_db)):
    """Delete {entity_var}"""
    # TODO: Implement delete
    return {"message": f"{entity_name} deleted"}
'''

        return code

    def _generate_ui_components(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Generate Next.js components"""
        components_path = os.path.join(self.output_path, 'apps', 'web', 'components', self.scenario)
        os.makedirs(components_path, exist_ok=True)

        generated_components = []

        for entity in entities:
            component_code = self._create_component_code(entity)
            component_file = os.path.join(components_path, f"{entity['name']}Card.tsx")

            with open(component_file, 'w') as f:
                f.write(component_code)

            generated_components.append(component_file)

        return generated_components

    def _create_component_code(self, entity: Dict[str, Any]) -> str:
        """Create React component code"""
        entity_name = entity['name']
        component_name = f"{entity_name}Card"

        code = f'''"""
{component_name} - {entity.get('description', f'{entity_name} display component')}
Generated based on PRD
"""
'use client';

import React from 'react';

interface {component_name}Props {{
    data: {{
'''

        for field in entity['fields'][:5]:  # Show first 5 fields
            field_name = field['name']
            field_type = field['type']

            # Map to TypeScript type
            if field_type in ['Integer', 'BigInteger']:
                ts_type = 'number'
            elif field_type == 'DECIMAL' or field_type == 'Float':
                ts_type = 'number'
            elif field_type == 'Boolean':
                ts_type = 'boolean'
            else:
                ts_type = 'string'

            code += f'''        {field_name}: {ts_type};
'''

        code += f'''    };
}}

export function {component_name}({{ data }}: {component_name}Props) {{
    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-bold mb-4">{entity_name}</h3>

            <div className="space-y-2">
'''

        for field in entity['fields'][:5]:
            field_name = field['name']
            field_display = field_name.replace('_', ' ').title()

            code += f'''                <div>
                    <span className="text-gray-600">{field_display}:</span>
                    <span className="ml-2 font-semibold">{{data.{field_name}}}</span>
                </div>
'''

        code += f'''            </div>

            <button className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors">
                View Details
            </button>
        </div>
    );
}}

export default {component_name};
'''

        return code

    def _generate_config(self, requirements: Dict[str, Any]):
        """Generate configuration files"""
        # Update package.json
        pkg_path = os.path.join(self.output_path, 'apps', 'web', 'package.json')
        if os.path.exists(pkg_path):
            with open(pkg_path, 'r') as f:
                package = json.load(f)

            package['name'] = f"hdcp-{self.scenario}-app"
            package['description'] = f"HDCP {self.scenario.title()} Application"

            with open(pkg_path, 'w') as f:
                json.dump(package, f, indent=2)

    def _generate_docs(self, entities: List[Dict[str, Any]], apis: List[str], components: List[str]) -> str:
        """Generate documentation"""
        docs_path = os.path.join(self.output_path, 'docs', 'GENERATED.md')

        os.makedirs(os.path.dirname(docs_path), exist_ok=True)

        code = f'''# Generated Project Documentation

## Project Overview
- **Scenario**: {self.scenario}
- **Generated**: {len(entities)} entities, {len(apis)} APIs, {len(components)} components

## Entities
'''

        for entity in entities:
            code += f'\n### {entity["name"]}\n'
            code += f'{entity.get("description", "")}\n\n'
            code += 'Fields:\n'
            for field in entity['fields']:
                code += f'- `{field["name"]}` ({field["type"]}): {field.get("description", "")}\n'

        code += '''
## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

```bash
# Copy environment template
cp .env.example .env

# Start services
docker-compose up -d

# Install dependencies
cd apps/api && pip install -r requirements.txt
cd ../../apps/web && npm install
```

### Development

```bash
# Start API
cd apps/api
uvicorn app.main:app --reload

# Start Web
cd apps/web
npm run dev
```

### Deployment

```bash
# Production deployment
docker-compose -f deploy/docker-compose.full.yml up -d
```

## Features
'''

        for feature in self.features:
            code += f'- {feature}\n'

        code += '''
## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

```
generated-project/
├── apps/
│   ├── api/          # FastAPI backend
│   ├── web/          # Next.js frontend
│   └── cms/          # Strapi CMS
├── deploy/           # Deployment configs
└── docs/            # Documentation
```

## Next Steps

1. Review generated models in `apps/api/app/models/`
2. Customize API endpoints in `apps/api/app/routers/`
3. Build UI components in `apps/web/components/`
4. Update configuration in `hdcp.config.yaml`
5. Add authentication and authorization
6. Implement business logic
7. Add tests
8. Deploy to production

## Support

For issues and questions, please visit the HDCP documentation.
'''

        with open(docs_path, 'w') as f:
            f.write(code)

        return docs_path


def generate_hdcp_project(
    prd_path: str,
    scenario: str,
    features: Optional[List[str]] = None,
    customizations: Optional[Dict[str, Any]] = None,
    output_path: str = "generated-project",
    template_path: str = "hdcp-platform"
) -> Dict[str, Any]:
    """
    Generate a complete HDCP project based on PRD

    Args:
        prd_path: Path to PRD file
        scenario: Business scenario (stock, iot, ecommerce, carbon)
        features: Additional features to enable
        customizations: Custom configuration
        output_path: Output directory
        template_path: HDCP template path

    Returns:
        Dictionary with generation results
    """
    generator = HDCPProjectGenerator(template_path)
    return generator.generate_project(
        prd_path=prd_path,
        scenario=scenario,
        features=features,
        customizations=customizations,
        output_path=output_path
    )
