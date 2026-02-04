"""Initial migration

Revision ID: 03f97757c4c1
Revises:
Create Date: 2026-02-04 12:31:46.390766

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '03f97757c4c1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stock_prices table
    op.create_table(
        'stock_prices',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('symbol', sa.String(length=20), nullable=False, comment='Stock symbol'),
        sa.Column('price', sa.Numeric(precision=10, scale=4), nullable=False, comment='Stock price'),
        sa.Column('volume', sa.BigInteger(), nullable=True, comment='Trading volume'),
        sa.Column('price_change', sa.Numeric(precision=10, scale=4), nullable=True, comment='Price change'),
        sa.Column('price_change_percent', sa.Numeric(precision=5, scale=2), nullable=True, comment='Price change %'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='Price timestamp'),
        sa.Column('source', sa.String(length=50), nullable=True, comment='Data source'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_stock_symbol_timestamp', 'symbol', 'timestamp'),
    )
    op.execute("COMMENT ON TABLE stock_prices IS 'Stock price data model'")
    op.execute("COMMENT ON COLUMN stock_prices.symbol IS 'Stock symbol'")
    op.execute("COMMENT ON COLUMN stock_prices.price IS 'Stock price'")
    op.execute("COMMENT ON COLUMN stock_prices.volume IS 'Trading volume'")
    op.execute("COMMENT ON COLUMN stock_prices.price_change IS 'Price change'")
    op.execute("COMMENT ON COLUMN stock_prices.price_change_percent IS 'Price change %'")
    op.execute("COMMENT ON COLUMN stock_prices.timestamp IS 'Price timestamp'")
    op.execute("COMMENT ON COLUMN stock_prices.source IS 'Data source'")

    # Create stock_indicators table
    op.create_table(
        'stock_indicators',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('symbol', sa.String(length=20), nullable=False, comment='Stock symbol'),
        sa.Column('indicator_type', sa.String(length=50), nullable=False, comment='Indicator type'),
        sa.Column('period', sa.Integer(), nullable=True, comment='Period for calculation'),
        sa.Column('value', sa.Numeric(precision=10, scale=4), nullable=False, comment='Indicator value'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='Calculation timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_indicator_symbol_type', 'symbol', 'indicator_type', 'timestamp'),
    )
    op.execute("COMMENT ON TABLE stock_indicators IS 'Technical indicators for stocks'")
    op.execute("COMMENT ON COLUMN stock_indicators.symbol IS 'Stock symbol'")
    op.execute("COMMENT ON COLUMN stock_indicators.indicator_type IS 'Indicator type'")
    op.execute("COMMENT ON COLUMN stock_indicators.period IS 'Period for calculation'")
    op.execute("COMMENT ON COLUMN stock_indicators.value IS 'Indicator value'")
    op.execute("COMMENT ON COLUMN stock_indicators.timestamp IS 'Calculation timestamp'")

    # Create sensor_readings table
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('sensor_id', sa.String(length=50), nullable=False, comment='Sensor ID'),
        sa.Column('location', sa.String(length=100), nullable=True, comment='Sensor location'),
        sa.Column('temperature', sa.Numeric(precision=5, scale=2), nullable=True, comment='Temperature (°C)'),
        sa.Column('humidity', sa.Numeric(precision=5, scale=2), nullable=True, comment='Humidity (%)'),
        sa.Column('battery_level', sa.Integer(), nullable=True, comment='Battery level (%)'),
        sa.Column('signal_strength', sa.Integer(), nullable=True, comment='Signal strength (dBm)'),
        sa.Column('sensor_metadata', sa.String(), nullable=True, comment='Additional sensor data'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='Reading timestamp'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='Sensor status'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_sensor_id_timestamp', 'sensor_id', 'timestamp'),
        sa.Index('idx_sensor_location', 'location'),
    )
    op.execute("COMMENT ON TABLE sensor_readings IS 'IoT sensor reading data model'")
    op.execute("COMMENT ON COLUMN sensor_readings.sensor_id IS 'Sensor ID'")
    op.execute("COMMENT ON COLUMN sensor_readings.location IS 'Sensor location'")
    op.execute("COMMENT ON COLUMN sensor_readings.temperature IS 'Temperature (°C)'")
    op.execute("COMMENT ON COLUMN sensor_readings.humidity IS 'Humidity (%)'")
    op.execute("COMMENT ON COLUMN sensor_readings.battery_level IS 'Battery level (%)'")
    op.execute("COMMENT ON COLUMN sensor_readings.signal_strength IS 'Signal strength (dBm)'")
    op.execute("COMMENT ON COLUMN sensor_readings.sensor_metadata IS 'Additional sensor data'")
    op.execute("COMMENT ON COLUMN sensor_readings.timestamp IS 'Reading timestamp'")
    op.execute("COMMENT ON COLUMN sensor_readings.status IS 'Sensor status'")

    # Create sensor_alerts table
    op.create_table(
        'sensor_alerts',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('sensor_id', sa.String(length=50), nullable=False, comment='Sensor ID'),
        sa.Column('alert_type', sa.String(length=50), nullable=False, comment='Alert type'),
        sa.Column('severity', sa.String(length=20), nullable=False, comment='Alert severity'),
        sa.Column('message', sa.String(length=255), nullable=False, comment='Alert message'),
        sa.Column('value', sa.Numeric(precision=10, scale=4), nullable=True, comment='Value that triggered alert'),
        sa.Column('threshold', sa.Numeric(precision=10, scale=4), nullable=True, comment='Threshold value'),
        sa.Column('resolved', sa.Boolean(), nullable=False, comment='Alert resolved status'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True, comment='Resolution timestamp'),
        sa.Column('resolved_by', sa.String(length=100), nullable=True, comment='Resolved by user'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_alert_sensor_resolved', 'sensor_id', 'resolved'),
        sa.Index('idx_alert_severity', 'severity'),
    )
    op.execute("COMMENT ON TABLE sensor_alerts IS 'Alerts generated from sensor readings'")

    # Create product_prices table
    op.create_table(
        'product_prices',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('product_id', sa.String(length=100), nullable=False, comment='Product ID'),
        sa.Column('product_name', sa.String(length=255), nullable=True, comment='Product name'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, comment='Product price'),
        sa.Column('currency', sa.String(length=3), nullable=True, comment='Currency code'),
        sa.Column('price_usd', sa.Numeric(precision=10, scale=2), nullable=True, comment='Price in USD'),
        sa.Column('exchange_rate', sa.Numeric(precision=10, scale=6), nullable=True, comment='Exchange rate'),
        sa.Column('source', sa.String(length=50), nullable=False, comment='E-commerce platform'),
        sa.Column('source_url', sa.Text(), nullable=True, comment='Product URL'),
        sa.Column('availability', sa.String(length=20), nullable=True, comment='Availability status'),
        sa.Column('stock_count', sa.Integer(), nullable=True, comment='Stock quantity'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='Product category'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='Price timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_product_id_timestamp', 'product_id', 'timestamp'),
        sa.Index('idx_product_source', 'source'),
        sa.Index('idx_product_category', 'category'),
    )
    op.execute("COMMENT ON TABLE product_prices IS 'Product price tracking model'")
    op.execute("COMMENT ON COLUMN product_prices.product_id IS 'Product ID'")
    op.execute("COMMENT ON COLUMN product_prices.product_name IS 'Product name'")
    op.execute("COMMENT ON COLUMN product_prices.price IS 'Product price'")
    op.execute("COMMENT ON COLUMN product_prices.currency IS 'Currency code'")
    op.execute("COMMENT ON COLUMN product_prices.price_usd IS 'Price in USD'")
    op.execute("COMMENT ON COLUMN product_prices.exchange_rate IS 'Exchange rate'")
    op.execute("COMMENT ON COLUMN product_prices.source IS 'E-commerce platform'")
    op.execute("COMMENT ON COLUMN product_prices.source_url IS 'Product URL'")
    op.execute("COMMENT ON COLUMN product_prices.availability IS 'Availability status'")
    op.execute("COMMENT ON COLUMN product_prices.stock_count IS 'Stock quantity'")
    op.execute("COMMENT ON COLUMN product_prices.category IS 'Product category'")
    op.execute("COMMENT ON COLUMN product_prices.timestamp IS 'Price timestamp'")

    # Create price_alerts table
    op.create_table(
        'price_alerts',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('product_id', sa.String(length=100), nullable=False, comment='Product ID'),
        sa.Column('target_price', sa.Numeric(precision=10, scale=2), nullable=False, comment='Target price'),
        sa.Column('current_price', sa.Numeric(precision=10, scale=2), nullable=False, comment='Current price'),
        sa.Column('price_drop_percent', sa.Numeric(precision=5, scale=2), nullable=False, comment='Drop percentage'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Alert email'),
        sa.Column('sent', sa.Boolean(), nullable=False, comment='Alert sent status'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True, comment='Alert sent timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_alert_product_sent', 'product_id', 'sent'),
    )
    op.execute("COMMENT ON TABLE price_alerts IS 'Price drop alerts for products'")
    op.execute("COMMENT ON COLUMN price_alerts.product_id IS 'Product ID'")
    op.execute("COMMENT ON COLUMN price_alerts.target_price IS 'Target price'")
    op.execute("COMMENT ON COLUMN price_alerts.current_price IS 'Current price'")
    op.execute("COMMENT ON COLUMN price_alerts.price_drop_percent IS 'Drop percentage'")
    op.execute("COMMENT ON COLUMN price_alerts.email IS 'Alert email'")
    op.execute("COMMENT ON COLUMN price_alerts.sent IS 'Alert sent status'")
    op.execute("COMMENT ON COLUMN price_alerts.sent_at IS 'Alert sent timestamp'")

    # Create carbon_credit_projects table
    op.create_table(
        'carbon_credit_projects',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('project_id', sa.String(length=100), nullable=False, unique=True, comment='Unique project ID'),
        sa.Column('project_name', sa.String(length=255), nullable=False, comment='Project name'),
        sa.Column('standard', sa.String(length=50), nullable=False, comment='Carbon standard'),
        sa.Column('location', sa.String(length=100), nullable=True, comment='Project location'),
        sa.Column('project_type', sa.String(length=100), nullable=True, comment='Project type'),
        sa.Column('additionality_score', sa.Numeric(precision=5, scale=2), nullable=True, comment='Additionality score'),
        sa.Column('co_benefits_score', sa.Numeric(precision=5, scale=2), nullable=True, comment='Co-benefits score'),
        sa.Column('total_credits', sa.Numeric(precision=15, scale=2), nullable=True, comment='Total carbon credits'),
        sa.Column('verified_credits', sa.Numeric(precision=15, scale=2), nullable=True, comment='Verified credits'),
        sa.Column('retired_credits', sa.Numeric(precision=15, scale=2), nullable=True, comment='Retired credits'),
        sa.Column('description', sa.Text(), nullable=True, comment='Project description'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_carbon_project_id', 'project_id'),
        sa.Index('idx_carbon_standard', 'standard'),
        sa.Index('idx_carbon_location', 'location'),
    )
    op.execute("COMMENT ON TABLE carbon_credit_projects IS 'Carbon credit project model'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.project_id IS 'Unique project ID'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.project_name IS 'Project name'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.standard IS 'Carbon standard'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.location IS 'Project location'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.project_type IS 'Project type'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.additionality_score IS 'Additionality score'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.co_benefits_score IS 'Co-benefits score'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.total_credits IS 'Total carbon credits'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.verified_credits IS 'Verified credits'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.retired_credits IS 'Retired credits'")
    op.execute("COMMENT ON COLUMN carbon_credit_projects.description IS 'Project description'")

    # Create carbon_credit_prices table
    op.create_table(
        'carbon_credit_prices',
        sa.Column('id', sa.Integer(), nullable=False, comment='Primary key'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='Update timestamp'),
        sa.Column('project_id', sa.String(length=100), nullable=False, comment='Project ID'),
        sa.Column('price_per_credit', sa.Numeric(precision=10, scale=2), nullable=False, comment='Price per credit'),
        sa.Column('currency', sa.String(length=3), nullable=True, comment='Currency code'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, comment='Price timestamp'),
        sa.Column('source', sa.String(length=100), nullable=True, comment='Price source'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_carbon_price_project_timestamp', 'project_id', 'timestamp'),
        sa.Index('idx_carbon_price_timestamp', 'timestamp'),
    )
    op.execute("COMMENT ON TABLE carbon_credit_prices IS 'Carbon credit price tracking'")
    op.execute("COMMENT ON COLUMN carbon_credit_prices.project_id IS 'Project ID'")
    op.execute("COMMENT ON COLUMN carbon_credit_prices.price_per_credit IS 'Price per credit'")
    op.execute("COMMENT ON COLUMN carbon_credit_prices.currency IS 'Currency code'")
    op.execute("COMMENT ON COLUMN carbon_credit_prices.timestamp IS 'Price timestamp'")
    op.execute("COMMENT ON COLUMN carbon_credit_prices.source IS 'Price source'")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('carbon_credit_prices')
    op.drop_table('carbon_credit_projects')
    op.drop_table('price_alerts')
    op.drop_table('product_prices')
    op.drop_table('sensor_alerts')
    op.drop_table('sensor_readings')
    op.drop_table('stock_indicators')
    op.drop_table('stock_prices')
