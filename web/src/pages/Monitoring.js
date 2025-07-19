import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Monitoring = () => {
  const { user } = useAuth();
  const [healthData, setHealthData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [slaMetrics, setSlaMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [config, setConfig] = useState(null);

  useEffect(() => {
    loadMonitoringData();
  }, []);

  const loadMonitoringData = async () => {
    try {
      setLoading(true);
      
      // Load health dashboard data
      const dashboardResponse = await api.get('/monitoring/health/dashboard');
      if (dashboardResponse.data.success) {
        setHealthData(dashboardResponse.data.dashboard_data.current_health);
        setAlerts(dashboardResponse.data.dashboard_data.recent_alerts);
        setIncidents(dashboardResponse.data.dashboard_data.active_incidents);
        setSlaMetrics(dashboardResponse.data.dashboard_data.sla_metrics);
      }
      
      // Load monitoring configuration
      const configResponse = await api.get('/monitoring/config');
      if (configResponse.data.success) {
        setConfig(configResponse.data.config);
      }
      
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await api.post(`/monitoring/alerts/${alertId}/acknowledge`);
      loadMonitoringData(); // Reload data
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      await api.post(`/monitoring/alerts/${alertId}/resolve`);
      loadMonitoringData(); // Reload data
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600 mt-2">Real-time health monitoring and alerting dashboard</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'alerts', name: 'Alerts' },
              { id: 'incidents', name: 'Incidents' },
              { id: 'sla', name: 'SLA Metrics' },
              { id: 'config', name: 'Configuration' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Health Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">System Status</p>
                    <p className={`text-2xl font-bold ${getStatusColor(healthData?.status)}`}>
                      {healthData?.status || 'Unknown'}
                    </p>
                  </div>
                  <div className="text-3xl">🖥️</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {healthData?.cpu_usage?.toFixed(1) || 0}%
                    </p>
                  </div>
                  <div className="text-3xl">⚡</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {healthData?.memory_usage?.toFixed(1) || 0}%
                    </p>
                  </div>
                  <div className="text-3xl">💾</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {healthData?.response_time?.toFixed(0) || 0}ms
                    </p>
                  </div>
                  <div className="text-3xl">⏱️</div>
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Uptime</span>
                    <span className="font-medium">{formatUptime(healthData?.uptime_seconds || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Connections</span>
                    <span className="font-medium">{healthData?.active_connections || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Error Rate</span>
                    <span className="font-medium">{(healthData?.error_rate || 0).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Throughput</span>
                    <span className="font-medium">{(healthData?.throughput || 0).toFixed(1)} req/s</span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h3>
                <div className="space-y-3">
                  {alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                        <p className="text-xs text-gray-500">{alert.message}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                  ))}
                  {alerts.length === 0 && (
                    <p className="text-gray-500 text-sm">No recent alerts</p>
                  )}
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Incidents</h3>
                <div className="space-y-3">
                  {incidents.slice(0, 5).map((incident) => (
                    <div key={incident.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{incident.title}</p>
                        <p className="text-xs text-gray-500">{incident.status}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                    </div>
                  ))}
                  {incidents.length === 0 && (
                    <p className="text-gray-500 text-sm">No active incidents</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">System Alerts</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {alerts.map((alert) => (
                <div key={alert.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-medium text-gray-900">{alert.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          alert.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {alert.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mt-2">{alert.message}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        Created: {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      {alert.status === 'active' && (
                        <>
                          <button
                            onClick={() => acknowledgeAlert(alert.id)}
                            className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200"
                          >
                            Acknowledge
                          </button>
                          <button
                            onClick={() => resolveAlert(alert.id)}
                            className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded hover:bg-green-200"
                          >
                            Resolve
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {alerts.length === 0 && (
                <div className="p-6 text-center text-gray-500">
                  No alerts found
                </div>
              )}
            </div>
          </div>
        )}

        {/* Incidents Tab */}
        {activeTab === 'incidents' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Active Incidents</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {incidents.map((incident) => (
                <div key={incident.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-medium text-gray-900">{incident.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                          {incident.severity}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          incident.status === 'open' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {incident.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mt-2">{incident.description}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        Detected: {new Date(incident.detected_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {incidents.length === 0 && (
                <div className="p-6 text-center text-gray-500">
                  No active incidents
                </div>
              )}
            </div>
          </div>
        )}

        {/* SLA Metrics Tab */}
        {activeTab === 'sla' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">SLA Compliance</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {slaMetrics.map((sla) => (
                  <div key={sla.name} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">{sla.name}</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Target</span>
                        <span className="font-medium">{sla.target}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current</span>
                        <span className="font-medium">{sla.current}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Compliance</span>
                        <span className={`font-medium ${
                          sla.compliance >= 100 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {sla.compliance.toFixed(2)}%
                        </span>
                      </div>
                      <div className="mt-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          sla.status === 'compliant' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {sla.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
                {slaMetrics.length === 0 && (
                  <div className="col-span-full text-center text-gray-500 py-8">
                    No SLA metrics available
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Monitoring Configuration</h2>
            </div>
            <div className="p-6">
              {config ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Alert Thresholds</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">CPU Warning</span>
                        <span className="font-medium">{config.cpu_warning_threshold}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CPU Critical</span>
                        <span className="font-medium">{config.cpu_critical_threshold}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Memory Warning</span>
                        <span className="font-medium">{config.memory_warning_threshold}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Memory Critical</span>
                        <span className="font-medium">{config.memory_critical_threshold}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Response Time Warning</span>
                        <span className="font-medium">{config.response_time_warning_threshold}ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Response Time Critical</span>
                        <span className="font-medium">{config.response_time_critical_threshold}ms</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">SLA Targets</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Uptime Target</span>
                        <span className="font-medium">{config.uptime_target}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Response Time Target</span>
                        <span className="font-medium">{config.response_time_target}ms</span>
                      </div>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4 mt-6">Notifications</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Email Notifications</span>
                        <span className={`font-medium ${config.email_notifications ? 'text-green-600' : 'text-red-600'}`}>
                          {config.email_notifications ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Slack Notifications</span>
                        <span className={`font-medium ${config.slack_notifications ? 'text-green-600' : 'text-red-600'}`}>
                          {config.slack_notifications ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Webhook Notifications</span>
                        <span className={`font-medium ${config.webhook_notifications ? 'text-green-600' : 'text-red-600'}`}>
                          {config.webhook_notifications ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Configuration not available
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Monitoring; 