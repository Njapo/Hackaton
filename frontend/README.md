# SkinAI Frontend

A modern, responsive web frontend for the SkinAI chatbot application.

## Features

- **Authentication**: Login and registration with JWT token management
- **Modern Chat Interface**: Clean, ChatGPT-style chat UI with message bubbles
- **Image Upload**: Drag-and-drop or click to upload skin images for analysis
- **Chat History**: View and access previous conversations in a sidebar
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Notifications**: Success, error, and warning notifications
- **Professional UI**: Modern gradient design with smooth animations

## Getting Started

1. **Start the Backend Server**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open the Frontend**:
   - Simply open `frontend/index.html` in your web browser
   - Or serve it using a local web server for better CORS handling

3. **Register/Login**:
   - Create a new account or login with existing credentials
   - The app will remember your session using localStorage

## Usage

1. **Upload an Image**: Click the camera icon to upload a skin image
2. **Describe Symptoms**: Type your symptoms or concerns in the message input
3. **Send for Analysis**: Click the send button to get AI-powered analysis
4. **View History**: Click the history button to see previous conversations
5. **Logout**: Use the logout button to end your session

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # All CSS styles and animations
├── app.js             # JavaScript application logic
└── README.md          # This file
```

## API Integration

The frontend integrates with the following backend endpoints:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login/json` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/ai/skin-analysis` - Upload image and get analysis
- `GET /api/ai/history` - Get chat history

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Features in Detail

### Authentication
- Secure JWT token-based authentication
- Automatic token validation and refresh
- Persistent login sessions
- Form validation and error handling

### Chat Interface
- Real-time message display with animations
- Image preview before sending
- Loading states and progress indicators
- Message timestamps
- Responsive message bubbles

### Chat History
- Sidebar with conversation history
- Click to load previous conversations
- Date and time stamps
- Message previews

### UI/UX
- Modern gradient design
- Smooth animations and transitions
- Mobile-responsive layout
- Accessibility features
- Professional color scheme

## Customization

You can easily customize the appearance by modifying `styles.css`:

- Change colors by updating CSS custom properties
- Modify animations by adjusting transition durations
- Update fonts by changing the Google Fonts import
- Adjust spacing and sizing as needed

## Troubleshooting

1. **CORS Issues**: Make sure your backend is running and CORS is properly configured
2. **API Connection**: Verify the API_BASE_URL in app.js matches your backend URL
3. **Image Upload**: Ensure images are in supported formats (JPG, PNG, etc.)
4. **Authentication**: Clear localStorage if you encounter auth issues

## Security Notes

- JWT tokens are stored in localStorage
- Images are processed client-side before upload
- All API calls include proper authentication headers
- Form validation prevents malicious input

Enjoy using SkinAI! 🚀
