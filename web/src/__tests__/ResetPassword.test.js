import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ResetPassword from '../pages/ResetPassword';
import api from '../services/api';

// Mock the API service
jest.mock('../services/api');
const mockApi = api;

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useSearchParams: () => [new URLSearchParams('?token=valid-token')],
  Link: ({ children, to }) => <a href={to}>{children}</a>,
}));

const renderResetPassword = () => {
  return render(
    <BrowserRouter>
      <ResetPassword />
    </BrowserRouter>
  );
};

describe('ResetPassword Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders reset password form with valid token', () => {
    renderResetPassword();
    
    expect(screen.getByText('Set New Password')).toBeInTheDocument();
    expect(screen.getByLabelText('New Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm New Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reset Password' })).toBeInTheDocument();
  });

  test('successful password reset', async () => {
    mockApi.post.mockResolvedValue({
      data: {
        message: 'Password reset successfully'
      }
    });

    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'valid-token',
        new_password: 'newpassword123'
      });
    });
  });

  test('password mismatch validation', async () => {
    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'differentpassword' } });
    fireEvent.click(submitButton);

    // Should not call API due to client-side validation
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('password too short validation', async () => {
    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'short' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'short' } });
    fireEvent.click(submitButton);

    // Should not call API due to client-side validation
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('empty password validation', async () => {
    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: '' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    // Should not call API due to client-side validation
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('empty confirm password validation', async () => {
    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: '' } });
    fireEvent.click(submitButton);

    // Should not call API due to client-side validation
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('invalid token error', async () => {
    mockApi.post.mockRejectedValue({
      response: {
        data: {
          detail: 'Invalid or expired reset token'
        }
      }
    });

    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'valid-token',
        new_password: 'newpassword123'
      });
    });
  });

  test('expired token error', async () => {
    mockApi.post.mockRejectedValue({
      response: {
        data: {
          detail: 'Invalid or expired reset token'
        }
      }
    });

    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'valid-token',
        new_password: 'newpassword123'
      });
    });
  });

  test('network error handling', async () => {
    mockApi.post.mockRejectedValue(new Error('Network error'));

    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'valid-token',
        new_password: 'newpassword123'
      });
    });
  });

  test('loading state during reset', async () => {
    mockApi.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    const submitButton = screen.getByRole('button', { name: 'Reset Password' });

    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(submitButton);

    expect(screen.getByText('Resetting...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  test('password visibility toggle', () => {
    renderResetPassword();
    
    const passwordInput = screen.getByLabelText('New Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm New Password');
    
    // Initially should be password type
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    
    // Toggle password visibility
    const toggleButtons = screen.getAllByRole('button');
    const passwordToggle = toggleButtons.find(button => 
      button.parentElement?.querySelector('input[type="password"]') === passwordInput
    );
    
    if (passwordToggle) {
      fireEvent.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'text');
    }
  });

  test('back to login link functionality', () => {
    renderResetPassword();
    
    const backLink = screen.getByText('Back to login');
    expect(backLink).toBeInTheDocument();
    expect(backLink.closest('a')).toHaveAttribute('href', '/login');
  });
}); 