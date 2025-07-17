import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../pages/ForgotPassword';
import api from '../services/api';

// Mock the API service
jest.mock('../services/api');
const mockApi = api;

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

const renderForgotPassword = () => {
  return render(
    <BrowserRouter>
      <ForgotPassword />
    </BrowserRouter>
  );
};

describe('ForgotPassword Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders forgot password form', () => {
    renderForgotPassword();
    
    expect(screen.getByText('Reset Password')).toBeInTheDocument();
    expect(screen.getByText('Enter your email address and we\'ll send you a link to reset your password.')).toBeInTheDocument();
    expect(screen.getByLabelText('Email address')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send Reset Link' })).toBeInTheDocument();
  });

  test('successful password reset request', async () => {
    mockApi.post.mockResolvedValue({
      data: {
        message: 'If the email exists, a password reset link has been sent'
      }
    });

    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/forgot-password', {
        email: 'test@example.com'
      });
    });

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument();
      expect(screen.getByText(/We've sent a password reset link to/)).toBeInTheDocument();
    });
  });

  test('password reset request with non-existent email', async () => {
    mockApi.post.mockResolvedValue({
      data: {
        message: 'If the email exists, a password reset link has been sent'
      }
    });

    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'nonexistent@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/forgot-password', {
        email: 'nonexistent@example.com'
      });
    });

    // Should still show success message for security
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument();
    });
  });

  test('network error handling', async () => {
    mockApi.post.mockRejectedValue(new Error('Network error'));

    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/forgot-password', {
        email: 'test@example.com'
      });
    });
  });

  test('server error handling', async () => {
    mockApi.post.mockRejectedValue({
      response: {
        data: {
          detail: 'Internal server error'
        }
      }
    });

    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/forgot-password', {
        email: 'test@example.com'
      });
    });
  });

  test('form validation - empty email', async () => {
    renderForgotPassword();
    
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    fireEvent.click(submitButton);

    // Client-side validation should prevent API call
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('form validation - invalid email format', async () => {
    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    // Client-side validation should prevent API call
    expect(mockApi.post).not.toHaveBeenCalled();
  });

  test('loading state during request', async () => {
    mockApi.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderForgotPassword();
    
    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    expect(screen.getByText('Sending...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  test('back to login link functionality', () => {
    renderForgotPassword();
    
    const backLink = screen.getByText('Back to login');
    expect(backLink).toBeInTheDocument();
    expect(backLink.closest('a')).toHaveAttribute('href', '/login');
  });
}); 