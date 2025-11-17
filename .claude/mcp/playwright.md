# MCP Playwright

Integration with Playwright for cross-browser automation, testing, and monitoring.

## Capabilities

- **Cross-Browser Testing**: Test on Chrome, Firefox, Safari, and Edge
- **API Testing**: Test REST APIs with full control
- **Visual Testing**: Screenshot comparison and visual regression
- **Network Interception**: Mock, modify, or inspect network traffic
- **Mobile Emulation**: Test responsive designs on mobile viewports
- **Accessibility Testing**: Automated a11y auditing

## Use Cases for AWS Monitoring Project

### 1. API Gateway Testing
```python
# Test API endpoints
async with async_playwright() as p:
    context = await p.request.new_context(
        base_url='https://api.example.com'
    )

    # Test event listing endpoint
    response = await context.get('/events')
    assert response.status == 200
    events = await response.json()

    # Test authentication
    response = await context.post('/events', headers={
        'Authorization': 'Bearer token'
    }, data={'event': 'data'})
```

### 2. Integration Testing
- Test Lambda function URLs
- Verify API Gateway responses
- Test webhook deliveries (Slack notifications)
- Validate error responses and status codes

### 3. Monitoring Dashboard Testing
- Test monitoring dashboard UI
- Verify real-time event updates
- Test filtering and pagination
- Validate data visualization
- Test responsive layouts

### 4. End-to-End Workflows
- Test complete event flow from creation to notification
- Verify agent deployment workflows
- Test error handling and recovery
- Validate multi-account scenarios

## Configuration

The Playwright MCP server enables:
- Headless browser automation
- API testing without browser
- Network traffic analysis
- Screenshot and video capture
- Parallel test execution

## Example Usage

### API Testing
```python
import asyncio
from playwright.async_api import async_playwright

async def test_events_api():
    async with async_playwright() as p:
        context = await p.request.new_context()

        # List events
        response = await context.get(
            'http://localhost:3000/events',
            params={'limit': 10}
        )
        assert response.status == 200

        # Create event
        response = await context.post(
            'http://localhost:3000/events',
            data={
                'account': '123456789012',
                'source': 'test',
                'detail': {}
            }
        )
        assert response.status == 201

asyncio.run(test_events_api())
```

### UI Testing
```python
async def test_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto('http://localhost:8080')
        await page.wait_for_selector('.event-list')

        # Verify events are displayed
        events = await page.locator('.event-item').count()
        assert events > 0

        # Test filtering
        await page.fill('#account-filter', '123456789012')
        await page.click('#apply-filter')
        await page.wait_for_load_state('networkidle')

        await browser.close()
```

## Integration Points

- Test API endpoints during development
- Validate webhook deliveries
- Test frontend integrations
- Perform visual regression testing
- Monitor API performance
- Test error scenarios
