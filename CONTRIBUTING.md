# Contributing to Financial Sentiment Analysis Dashboard

Thank you for your interest in contributing to our project! This document provides guidelines for contributing to the Financial Sentiment Analysis Dashboard.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/financial-sentiment-dashboard.git
   cd financial-sentiment-dashboard
   ```
3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Test your changes**
6. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

## 📋 Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for backend development)

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Run all tests
./scripts/run-tests.sh

# Run specific tests
./scripts/run-tests.sh backend
./scripts/run-tests.sh frontend
```

## 🎯 Areas for Contribution

### High Priority
- **Bug fixes** - Any issues reported in GitHub Issues
- **Documentation** - Improving README, API docs, code comments
- **Tests** - Adding test coverage for existing features
- **Performance** - Optimizing database queries, API responses

### Medium Priority
- **New features** - Adding new dashboard components
- **UI/UX improvements** - Better responsive design, accessibility
- **Data sources** - Integrating new financial data APIs
- **Monitoring** - Enhanced logging and metrics

### Low Priority
- **Code refactoring** - Improving code structure and organization
- **Dependencies** - Updating to latest versions
- **CI/CD** - Improving deployment pipelines

## 📝 Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all functions
- Maximum line length: 88 characters (Black formatter)

```python
def calculate_sentiment_score(text: str) -> float:
    """
    Calculate sentiment score for given text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Sentiment score between -1 and 1
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)
- Use functional components with hooks
- Follow ESLint configuration
- Use TypeScript for new components
- Write meaningful component and function names

```javascript
const SentimentChart = ({ data, onDataPointClick }) => {
  const [loading, setLoading] = useState(false);
  
  // Component logic here
  
  return (
    <div className="sentiment-chart">
      {/* JSX here */}
    </div>
  );
};
```

### CSS
- Use BEM methodology for class naming
- Prefer CSS Grid and Flexbox over floats
- Mobile-first responsive design
- Use CSS custom properties for theming

```css
.sentiment-chart {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

.sentiment-chart__header {
  font-size: 1.25rem;
  font-weight: 600;
}
```

## 🧪 Testing Guidelines

### Backend Tests
- Write unit tests for all new functions
- Use pytest fixtures for test data
- Mock external API calls
- Test both success and error cases

```python
def test_calculate_sentiment_score():
    """Test sentiment score calculation."""
    text = "This is a positive message"
    score = calculate_sentiment_score(text)
    assert 0 <= score <= 1
```

### Frontend Tests
- Test component rendering
- Test user interactions
- Mock API calls
- Test error states

```javascript
it('renders sentiment chart with data', () => {
  const mockData = [{ sentiment: 0.5, date: '2024-01-01' }];
  render(<SentimentChart data={mockData} />);
  expect(screen.getByText('Sentiment Chart')).toBeInTheDocument();
});
```

## 📊 Database Changes

When making database changes:

1. **Create a migration script**
2. **Update the schema documentation**
3. **Test with sample data**
4. **Update related API endpoints**

## 🔐 Security Guidelines

- Never commit API keys or sensitive data
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication and authorization
- Follow OWASP security guidelines

## 📚 Documentation

When adding new features:

1. **Update README.md** with new functionality
2. **Add API documentation** for new endpoints
3. **Include usage examples**
4. **Update project structure diagram**

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Environment details** (OS, browser, etc.)
5. **Screenshots** if applicable

## 💡 Feature Requests

When requesting features:

1. **Clear description** of the feature
2. **Use case** and benefits
3. **Mockups or wireframes** if applicable
4. **Priority level** (High/Medium/Low)

## 🤝 Pull Request Guidelines

### Before submitting a PR:

1. **Test your changes** thoroughly
2. **Update documentation** if needed
3. **Follow the code style** guidelines
4. **Write meaningful commit messages**
5. **Keep PRs focused** on a single feature/fix

### PR Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **GitHub contributors** page
- **Release notes** for significant contributions

## 📞 Getting Help

If you need help:

- 📧 **Email**: [your-email@example.com]
- 💬 **Discussions**: [GitHub Discussions](https://github.com/hugo9917/financial-sentiment-dashboard/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/hugo9917/financial-sentiment-dashboard/issues)

Thank you for contributing to our project! 🎉 