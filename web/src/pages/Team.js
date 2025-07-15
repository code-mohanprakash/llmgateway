import React, { useState, useEffect } from 'react';
import { 
  UserPlusIcon, 
  PencilIcon, 
  TrashIcon, 
  UserIcon,
  ShieldCheckIcon,
  EyeIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';
import toast from 'react-hot-toast';
import RoleBasedAccess from '../components/RoleBasedAccess';

const Team = () => {
  const [users, setUsers] = useState([]);
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    full_name: '',
    role: 'member'
  });
  const [editForm, setEditForm] = useState({
    full_name: '',
    role: '',
    is_active: true
  });

  const roles = [
    { value: 'owner', label: 'Owner', description: 'Full access to all features', icon: ShieldCheckIcon },
    { value: 'admin', label: 'Admin', description: 'Manage team and settings', icon: CogIcon },
    { value: 'member', label: 'Member', description: 'Use API and view analytics', icon: UserIcon },
    { value: 'viewer', label: 'Viewer', description: 'View-only access', icon: EyeIcon }
  ];

  useEffect(() => {
    fetchTeamData();
  }, []);

  const fetchTeamData = async () => {
    try {
      setLoading(true);
      const [usersResponse, orgResponse] = await Promise.all([
        api.get('/auth/users'),
        api.get('/auth/organization')
      ]);
      setUsers(usersResponse.data);
      setOrganization(orgResponse.data);
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
      toast.error(message || 'Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  const handleInviteUser = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/users/invite', inviteForm);
      toast.success('User invited successfully!');
      setShowInviteModal(false);
      setInviteForm({ email: '', full_name: '', role: 'member' });
      fetchTeamData();
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
      toast.error(message || 'Failed to invite user');
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/auth/users/${selectedUser.id}`, editForm);
      toast.success('User updated successfully!');
      setShowEditModal(false);
      setSelectedUser(null);
      setEditForm({ full_name: '', role: '', is_active: true });
      fetchTeamData();
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
      toast.error(message || 'Failed to update user');
    }
  };

  const handleRemoveUser = async (userId) => {
    if (!window.confirm('Are you sure you want to remove this user?')) {
      return;
    }
    
    try {
      await api.delete(`/auth/users/${userId}`);
      toast.success('User removed successfully!');
      fetchTeamData();
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
      toast.error(message || 'Failed to remove user');
    }
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setEditForm({
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active
    });
    setShowEditModal(true);
  };

  const getRoleInfo = (roleValue) => {
    return roles.find(role => role.value === roleValue) || roles[2];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <RoleBasedAccess requireAdmin={true} fallback={
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
          <p className="text-gray-500">You need admin permissions to access team management.</p>
        </div>
      </div>
    }>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Team Management</h1>
            <p className="text-gray-600 mt-1">
              Manage your team members and their roles
            </p>
          </div>
          <button
            onClick={() => setShowInviteModal(true)}
            className="btn-primary flex items-center"
          >
            <UserPlusIcon className="h-5 w-5 mr-2" />
            Invite User
          </button>
        </div>

        {/* Organization Info */}
        {organization && (
          <div className="clean-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium">{organization.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Plan</p>
                <p className="font-medium capitalize">{organization.plan_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Team Members</p>
                <p className="font-medium">{organization.user_count}</p>
              </div>
            </div>
          </div>
        )}

        {/* Team Members */}
        <div className="clean-card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Team Members</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => {
                  const roleInfo = getRoleInfo(user.role);
                  const RoleIcon = roleInfo.icon;
                  
                  return (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                              {user.full_name[0]}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.full_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {user.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <RoleIcon className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900 capitalize">
                            {roleInfo.label}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => openEditModal(user)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          {user.role !== 'owner' && (
                            <button
                              onClick={() => handleRemoveUser(user.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Invite User Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="clean-card max-w-md w-full mx-4">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Invite User</h3>
              </div>
              <form onSubmit={handleInviteUser} className="px-6 py-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({...inviteForm, email: e.target.value})}
                    className="form-input"
                    placeholder="user@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={inviteForm.full_name}
                    onChange={(e) => setInviteForm({...inviteForm, full_name: e.target.value})}
                    className="form-input"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <select
                    value={inviteForm.role}
                    onChange={(e) => setInviteForm({...inviteForm, role: e.target.value})}
                    className="form-input"
                  >
                    {roles.map((role) => (
                      <option key={role.value} value={role.value}>
                        {role.label} - {role.description}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Invite User
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {showEditModal && selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="clean-card max-w-md w-full mx-4">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Edit User</h3>
              </div>
              <form onSubmit={handleEditUser} className="px-6 py-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={editForm.full_name}
                    onChange={(e) => setEditForm({...editForm, full_name: e.target.value})}
                    className="form-input"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <select
                    value={editForm.role}
                    onChange={(e) => setEditForm({...editForm, role: e.target.value})}
                    className="form-input"
                  >
                    {roles.map((role) => (
                      <option key={role.value} value={role.value}>
                        {role.label} - {role.description}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_active}
                      onChange={(e) => setEditForm({...editForm, is_active: e.target.checked})}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Active</span>
                  </label>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Update User
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </RoleBasedAccess>
  );
};

export default Team; 