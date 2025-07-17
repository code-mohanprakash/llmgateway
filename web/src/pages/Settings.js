import React, { useState, useEffect } from 'react';
import { UserIcon, CogIcon, ShieldCheckIcon, BellIcon, LockClosedIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    organizationName: '',
    timezone: 'America/New_York',
    language: 'en'
  });

  const [apiSettings, setApiSettings] = useState({
    defaultModel: '',
    defaultProvider: '',
    maxTokens: 4000,
    temperature: 0.7,
    timeout: 30,
    retryAttempts: 3
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorEnabled: false,
    sessionTimeout: 24,
    ipWhitelisting: false,
    allowedIPs: '',
    loginAlerts: true
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailAlerts: true,
    usageAlerts: true,
    billingAlerts: true,
    securityAlerts: true,
    marketingEmails: false,
    usageThreshold: 80
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'api', name: 'API Configuration', icon: CogIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon }
  ];

  useEffect(() => {
    // Disable API call until working auth integration is complete
    // fetchSettings();
    
    // Set default values for now
    setProfile({
      email: user?.email || '',
      firstName: user?.first_name || '',
      lastName: user?.last_name || '',
      organizationName: user?.organization || 'My Organization'
    });
    setLoading(false);
  }, [user]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/auth/me');
      const userData = response.data;
      
      setProfileData({
        firstName: userData.firstName || '',
        lastName: userData.lastName || '',
        email: userData.email || '',
        organizationName: userData.organization?.name || '',
        timezone: userData.timezone || 'America/New_York',
        language: userData.language || 'en'
      });
    } catch (error) {
      let message = error.response?.data?.detail;
      if (!message && error.response?.data && typeof error.response.data === 'object') {
        if (Array.isArray(error.response.data)) {
          message = error.response.data.map(e => e.msg).join(', ');
        } else if (error.response.data.detail) {
          message = error.response.data.detail;
        } else {
          message = JSON.stringify(error.response.data);
        }
      }
      toast.error(message || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (section) => {
    try {
      let endpoint = '';
      let data = {};
      
      switch (section) {
        case 'Profile':
          endpoint = '/auth/profile';
          data = profileData;
          break;
        case 'API':
          endpoint = '/auth/api-settings';
          data = apiSettings;
          break;
        case 'Security':
          endpoint = '/auth/security-settings';
          data = securitySettings;
          break;
        case 'Notifications':
          endpoint = '/auth/notification-settings';
          data = notificationSettings;
          break;
      }
      
      await api.put(endpoint, data);
      toast.success(`${section} settings saved successfully!`);
    } catch (error) {
      console.error(`Failed to save ${section.toLowerCase()} settings:`, error);
      toast.error(`Failed to save ${section.toLowerCase()} settings`);
    }
  };

  const ProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
        <p className="text-sm text-gray-600">Update your personal and organization details.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
          <input
            type="text"
            value={profileData.firstName}
            onChange={(e) => setProfileData({...profileData, firstName: e.target.value})}
            className="form-input"
            placeholder="Enter your first name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
          <input
            type="text"
            value={profileData.lastName}
            onChange={(e) => setProfileData({...profileData, lastName: e.target.value})}
            className="form-input"
            placeholder="Enter your last name"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
        <input
          type="email"
          value={profileData.email}
          onChange={(e) => setProfileData({...profileData, email: e.target.value})}
          className="form-input"
          placeholder="Enter your email address"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Organization Name</label>
        <input
          type="text"
          value={profileData.organizationName}
          onChange={(e) => setProfileData({...profileData, organizationName: e.target.value})}
          className="form-input"
          placeholder="Enter your organization name"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
          <select
            value={profileData.timezone}
            onChange={(e) => setProfileData({...profileData, timezone: e.target.value})}
            className="form-input"
          >
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
          <select
            value={profileData.language}
            onChange={(e) => setProfileData({...profileData, language: e.target.value})}
            className="form-input"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handleSave('Profile')}
          className="btn-primary px-8 text-lg"
        >
          Save Changes
        </button>
      </div>
    </div>
  );

  const APITab = () => {
    const [models, setModels] = useState([]);
    const [planType, setPlanType] = useState('free');
    const [selectedModel, setSelectedModel] = useState('');
    const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
    const [loadingModels, setLoadingModels] = useState(true);

    useEffect(() => {
      // Disable API call until working auth integration is complete
      // const fetchModels = async () => {
      //   setLoadingModels(true);
      //   try {
      //     const res = await api.get('/v1/models');
      //     // Flatten models into a list with plan_required
      //     let allModels = [];
      //     Object.entries(res.data.models).forEach(([provider, models]) => {
      //       models.forEach((model) => {
      //         allModels.push({ ...model, provider });
      //       });
      //     });
      //     setModels(allModels);
      //     setPlanType(res.data.plan_type);
      //   } catch (err) {
      //     toast.error('Failed to load models');
      //   } finally {
      //     setLoadingModels(false);
      //   }
      // };
      // fetchModels();
      
      // Set empty state for now
      setModels([]);
      setPlanType('free');
      setLoadingModels(false);
    }, []);

    const handleModelChange = (e) => {
      const modelId = e.target.value;
      const model = models.find((m) => m.model_id === modelId);
      if (model.plan_required === 'paid' && planType === 'free') {
        setShowUpgradePrompt(true);
        return;
      }
      setSelectedModel(modelId);
      setApiSettings((prev) => ({ ...prev, defaultModel: modelId }));
    };

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">API Configuration</h3>
          <p className="text-sm text-gray-600">Configure default settings for your API requests.</p>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Default Model</label>
          {loadingModels ? (
            <div className="animate-pulse h-10 bg-gray-100 rounded" />
          ) : (
            <select
              value={selectedModel}
              onChange={handleModelChange}
              className="form-input w-full"
            >
              <option value="">Select a model</option>
              {models.map((model) => (
                <option
                  key={model.model_id}
                  value={model.model_id}
                  disabled={model.plan_required === 'paid' && planType === 'free'}
                >
                  {model.model_name} ({model.provider})
                  {model.plan_required === 'paid' ? ' (Paid)' : ' (Free)'}
                </option>
              ))}
            </select>
          )}
          <div className="mt-2 flex flex-wrap gap-2">
            {models.map((model) =>
              model.plan_required === 'paid' && planType === 'free' ? (
                <span key={model.model_id} className="inline-flex items-center px-2 py-1 bg-gray-200 text-gray-500 rounded text-xs">
                  <LockClosedIcon className="h-4 w-4 mr-1" />
                  {model.model_name} ({model.provider})
                </span>
              ) : null
            )}
          </div>
          {showUpgradePrompt && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center justify-between">
              <div className="flex items-center">
                <LockClosedIcon className="h-6 w-6 text-yellow-500 mr-2" />
                <span className="text-yellow-700 text-sm font-medium">
                  This model requires a paid plan. Upgrade to unlock premium models like GPT-4, Claude, and more.
                </span>
              </div>
              <button
                className="btn-primary ml-4"
                onClick={() => window.location.href = '/billing'}
              >
                Upgrade Now
              </button>
            </div>
          )}
        </div>

        <div className="mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
            <CheckCircleIcon className="h-4 w-4 mr-1" />
            Current Plan: {planType.charAt(0).toUpperCase() + planType.slice(1)}
          </span>
          {planType === 'free' && (
            <button
              className="btn-primary ml-4"
              onClick={() => window.location.href = '/billing'}
            >
              Upgrade for More Models
            </button>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Configuration Notice</h4>
          <p className="text-sm text-blue-700">
            API settings will be available once you start making requests to the Model Bridge.
          </p>
        </div>

        <div className="flex justify-end">
          <button
            onClick={() => handleSave('API')}
            className="btn-primary px-8 text-lg"
          >
            Save Changes
          </button>
        </div>
      </div>
    );
  };

  const SecurityTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Security Settings</h3>
        <p className="text-sm text-gray-600">Manage your account security and access controls.</p>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex">
          <ShieldCheckIcon className="h-5 w-5 text-purple-500 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-purple-900">Security Recommendations</h4>
            <p className="text-sm text-purple-700 mt-1">
              Enable two-factor authentication and IP whitelisting for enhanced security.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
            <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
          </div>
          <button
            onClick={() => setSecuritySettings({...securitySettings, twoFactorEnabled: !securitySettings.twoFactorEnabled})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              securitySettings.twoFactorEnabled ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                securitySettings.twoFactorEnabled ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (hours)</label>
          <input
            type="number"
            value={securitySettings.sessionTimeout}
            onChange={(e) => setSecuritySettings({...securitySettings, sessionTimeout: parseInt(e.target.value)})}
            className="form-input"
            min="1"
            max="168"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handleSave('Security')}
          className="btn-primary px-8 text-lg"
        >
          Save Changes
        </button>
      </div>
    </div>
  );

  const NotificationsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
        <p className="text-sm text-gray-600">Choose what notifications you want to receive.</p>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Email Alerts</h4>
            <p className="text-sm text-gray-600">Receive important notifications via email</p>
          </div>
          <button
            onClick={() => setNotificationSettings({...notificationSettings, emailAlerts: !notificationSettings.emailAlerts})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              notificationSettings.emailAlerts ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                notificationSettings.emailAlerts ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Usage Alerts</h4>
            <p className="text-sm text-gray-600">Get notified when approaching usage limits</p>
          </div>
          <button
            onClick={() => setNotificationSettings({...notificationSettings, usageAlerts: !notificationSettings.usageAlerts})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              notificationSettings.usageAlerts ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                notificationSettings.usageAlerts ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Billing Alerts</h4>
            <p className="text-sm text-gray-600">Get notified about billing and payment issues</p>
          </div>
          <button
            onClick={() => setNotificationSettings({...notificationSettings, billingAlerts: !notificationSettings.billingAlerts})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              notificationSettings.billingAlerts ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                notificationSettings.billingAlerts ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Security Alerts</h4>
            <p className="text-sm text-gray-600">Get notified about security events and login attempts</p>
          </div>
          <button
            onClick={() => setNotificationSettings({...notificationSettings, securityAlerts: !notificationSettings.securityAlerts})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              notificationSettings.securityAlerts ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                notificationSettings.securityAlerts ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Marketing Emails</h4>
            <p className="text-sm text-gray-600">Receive updates about new features and announcements</p>
          </div>
          <button
            onClick={() => setNotificationSettings({...notificationSettings, marketingEmails: !notificationSettings.marketingEmails})}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2 ${
              notificationSettings.marketingEmails ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                notificationSettings.marketingEmails ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Usage Alert Threshold (%)</label>
          <input
            type="number"
            value={notificationSettings.usageThreshold}
            onChange={(e) => setNotificationSettings({...notificationSettings, usageThreshold: parseInt(e.target.value)})}
            className="form-input"
            min="10"
            max="100"
          />
        </div>
      </div>

      {/* Email Testing Section */}
      <div className="border-t border-gray-200 pt-6">
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900">Email Configuration Testing</h4>
          <p className="text-sm text-gray-600">Test your email configuration to ensure notifications are working properly.</p>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <CheckCircleIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h5 className="text-sm font-medium text-blue-900">Email Service Status</h5>
              <p className="text-sm text-blue-700 mt-1">
                SMTP configuration is properly set up and ready to send notifications.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={async () => {
              try {
                const response = await api.post('/auth/test-email', {
                  email: profileData.email,
                  test_type: 'password_reset'
                });
                toast.success('Test email sent successfully! Check your inbox.');
              } catch (error) {
                toast.error('Failed to send test email. Please check your email configuration.');
              }
            }}
            className="btn-secondary"
          >
            Send Test Password Reset Email
          </button>
          
          <button
            onClick={async () => {
              try {
                const response = await api.post('/auth/test-email', {
                  email: profileData.email,
                  test_type: 'verification'
                });
                toast.success('Test verification email sent successfully! Check your inbox.');
              } catch (error) {
                toast.error('Failed to send test email. Please check your email configuration.');
              }
            }}
            className="btn-secondary"
          >
            Send Test Verification Email
          </button>
          
          <button
            onClick={async () => {
              try {
                const response = await api.post('/auth/test-email', {
                  email: profileData.email,
                  test_type: 'notification'
                });
                toast.success('Test notification email sent successfully! Check your inbox.');
              } catch (error) {
                toast.error('Failed to send test email. Please check your email configuration.');
              }
            }}
            className="btn-secondary"
          >
            Send Test Notification Email
          </button>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handleSave('Notifications')}
          className="btn-primary px-8 text-lg"
        >
          Save Changes
        </button>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileTab />;
      case 'api':
        return <APITab />;
      case 'security':
        return <SecurityTab />;
      case 'notifications':
        return <NotificationsTab />;
      default:
        return <ProfileTab />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 gradient-text">Settings</h1>
            <p className="text-gray-600 mt-1">Manage your account preferences and configurations</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-300 border-t-gray-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 gradient-text">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account preferences and configurations</p>
      </div>

      <div className="lg:grid lg:grid-cols-12 lg:gap-x-5">
        <aside className="py-6 px-2 sm:px-6 lg:py-0 lg:px-0 lg:col-span-3">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-transparent text-gray-700 hover:bg-blue-50 hover:text-blue-800'
                  } group border-l-4 px-3 py-2 flex items-center text-sm font-medium w-full text-left transition-all duration-200 rounded-r-lg`}
                >
                  <Icon className="text-gray-500 group-hover:text-blue-600 flex-shrink-0 -ml-1 mr-3 h-6 w-6" />
                  <span className="truncate">{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        <div className="space-y-6 sm:px-6 lg:px-0 lg:col-span-9">
          <div className="clean-card rounded-2xl shadow-md">
            <div className="px-6 py-6">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;