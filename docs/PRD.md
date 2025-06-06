# Trade Blotter - Product Requirements Document (PRD)

## 1. Product Overview
Trade Blotter is a trading journal application designed to help traders log, analyze, and improve their trading performance through systematic trade tracking and analysis.

## 2. User Stories

### Core User Story
"As a trader, I want to log and tag my trades, so I can analyze my performance over time."

### Detailed User Stories
1. "As a trader, I want to manually enter my trades with key details, so I can maintain an accurate record of my trading activity."
2. "As a trader, I want to add custom tags to my trades, so I can categorize and analyze my trading patterns."
3. "As a trader, I want to view basic analytics about my trading performance, so I can identify areas for improvement."
4. "As a trader, I want to export my trade data, so I can perform additional analysis or maintain backups."
5. "As a trader, I want to view a dashboard with performance charts, so I can quickly assess my trading results."
6. "As a trader, I want to automatically import my trades from my brokerage, so I can save time and reduce manual entry errors."
7. "As a trader, I want to add detailed journal entries for each trade, so I can document my thought process and learn from my decisions."
8. "As a trader, I want to see my P/L broken down by different time periods, so I can better understand my trading patterns."

## 3. MVP Feature Set

### 3.1 Trade Entry
- Manual trade entry form with fields:
  - Symbol (required)
  - Date/Time (required)
  - Direction (Long/Short) (required)
  - Entry Price (required)
  - Exit Price (required)
  - Position Size (required)
  - Notes (optional)
  - Tags (multiple, optional)

### 3.2 Journal System
- Flexible journal entries:
  - Free-form text entry
  - Optional trade association
  - Timestamp for each entry
  - Daily journal entries without trade association
  - Rich text formatting
  - Image attachments
  - Tag support for entries
- Features:
  - Calendar view of entries
  - Search functionality
  - Filter by date, tags, or associated trades
  - Export journal entries
  - Link multiple trades to a single entry
  - Link multiple entries to a single trade

### 3.3 Brokerage Integration
- Support for three major brokerages:
  - Charles Schwab
  - Interactive Brokers (IBKR)
  - Tastyworks
- Features:
  - OAuth-based authentication
  - Automatic trade import
  - Daily position sync
  - Account balance tracking
  - Historical trade import

### 3.4 Analytics
- Basic performance metrics:
  - Win rate
  - Average win/loss
  - P&L per tag
  - Total P&L
  - Number of trades
  - Average holding time
- Time-based P/L analysis:
  - Daily P/L breakdown
  - Monthly P/L breakdown
  - P/L by time of day
  - P/L by day of week
  - Rolling P/L charts

### 3.5 Dashboard
- Key metrics summary
- P&L charts:
  - Daily breakdown
  - Monthly breakdown
  - Cumulative P/L
- Win rate chart
- Tag performance breakdown
- Recent trades list
- Journal entry highlights
- Brokerage account summary

### 3.6 Data Export
- CSV export
- JSON export
- Export filters (date range, tags, etc.)
- Journal entry export
- Brokerage reconciliation reports

## 4. Implementation Phases

### Phase 1: Core Infrastructure
- Project setup
- Database setup
- Authentication
- Basic API structure

### Phase 2: Trade Management
- Trade entry form
- Trade list view
- Basic CRUD operations
- Journal entry system

### Phase 3: Brokerage Integration
- Brokerage API integration
- Trade import system
- Account sync
- Data reconciliation

### Phase 4: Tagging System
- Tag management
- Trade tagging
- Tag-based filtering

### Phase 5: Analytics
- Basic metrics calculation
- Time-based P/L analysis
- Journal analysis
- Dashboard implementation
- Charts and visualizations

### Phase 6: Export & Polish
- Data export functionality
- UI/UX improvements
- Performance optimization

## 5. Success Metrics
- Number of trades logged
- User engagement (frequency of use)
- Export usage
- Tag usage statistics
- User retention
- Brokerage integration usage
- Journal entry completion rate

## 6. Future Considerations
- Additional brokerage integrations
- Advanced analytics
- Trade screenshot uploads
- AI-powered insights
- Mobile app
- Social features
- Trade idea sharing 