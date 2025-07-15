'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BrainIcon,
  UploadIcon,
  TargetIcon,
  BellIcon,
  BarChart3Icon,
  UserIcon,
  FileTextIcon,
  BriefcaseIcon,
  TrendingUpIcon,
  CalendarIcon,
  MapPinIcon,
  DollarSignIcon,
  StarIcon,
  ExternalLinkIcon
} from 'lucide-react';

// Mock data for demo purposes
const mockUser = {
  name: 'John Doe',
  email: 'john@example.com',
  profileCompletion: 85
};

const mockStats = {
  totalApplications: 12,
  pendingApplications: 5,
  interviewsScheduled: 2,
  offersReceived: 1,
  totalMatches: 34,
  newMatchesToday: 3
};

const mockMatches = [
  {
    id: 1,
    title: 'Senior Software Engineer',
    company: 'TechCorp Inc.',
    location: 'San Francisco, CA',
    salary: '$120,000 - $150,000',
    matchScore: 92,
    matchingSkills: ['React', 'Node.js', 'TypeScript', 'AWS'],
    postedDate: '2 hours ago',
    workType: 'Remote'
  },
  {
    id: 2,
    title: 'Full Stack Developer',
    company: 'StartupXYZ',
    location: 'New York, NY',
    salary: '$100,000 - $130,000',
    matchScore: 88,
    matchingSkills: ['Python', 'Django', 'PostgreSQL', 'Docker'],
    postedDate: '1 day ago',
    workType: 'Hybrid'
  },
  {
    id: 3,
    title: 'Frontend Engineer',
    company: 'Design Studio',
    location: 'Austin, TX',
    salary: '$90,000 - $120,000',
    matchScore: 85,
    matchingSkills: ['React', 'Vue.js', 'CSS', 'JavaScript'],
    postedDate: '2 days ago',
    workType: 'Onsite'
  }
];

const mockApplications = [
  {
    id: 1,
    jobTitle: 'Senior React Developer',
    company: 'Meta',
    status: 'Interview',
    appliedDate: '2024-01-15',
    lastUpdate: '2024-01-20'
  },
  {
    id: 2,
    jobTitle: 'Full Stack Engineer',
    company: 'Google',
    status: 'Applied',
    appliedDate: '2024-01-18',
    lastUpdate: '2024-01-18'
  },
  {
    id: 3,
    jobTitle: 'Software Engineer',
    company: 'Apple',
    status: 'Rejected',
    appliedDate: '2024-01-10',
    lastUpdate: '2024-01-17'
  }
];

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'interview': return 'bg-blue-100 text-blue-800';
    case 'applied': return 'bg-yellow-100 text-yellow-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    case 'offered': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getMatchScoreColor = (score: number) => {
  if (score >= 90) return 'text-green-600 bg-green-100';
  if (score >= 80) return 'text-blue-600 bg-blue-100';
  if (score >= 70) return 'text-yellow-600 bg-yellow-100';
  return 'text-gray-600 bg-gray-100';
};

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <BrainIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">WorkWale.ai</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="relative p-2 text-gray-400 hover:text-gray-500">
                <BellIcon className="w-6 h-6" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400"></span>
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <UserIcon className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-sm font-medium text-gray-700">{mockUser.name}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {mockUser.name}! 👋
          </h2>
          <p className="text-gray-600">
            Here's what's happening with your job search today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              label: 'Total Applications',
              value: mockStats.totalApplications,
              icon: FileTextIcon,
              color: 'bg-blue-500',
              change: '+2 this week'
            },
            {
              label: 'Job Matches',
              value: mockStats.totalMatches,
              icon: TargetIcon,
              color: 'bg-green-500',
              change: `+${mockStats.newMatchesToday} today`
            },
            {
              label: 'Interviews',
              value: mockStats.interviewsScheduled,
              icon: CalendarIcon,
              color: 'bg-purple-500',
              change: '1 upcoming'
            },
            {
              label: 'Offers',
              value: mockStats.offersReceived,
              icon: TrendingUpIcon,
              color: 'bg-orange-500',
              change: 'New!'
            }
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white p-6 rounded-lg shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <stat.icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs text-green-600 font-medium">{stat.change}</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white p-6 rounded-lg shadow-sm"
          >
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <UploadIcon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Resume</h3>
              <p className="text-sm text-gray-600 mb-4">
                Update your resume to get better job matches
              </p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Upload New Resume
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-white p-6 rounded-lg shadow-sm"
          >
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <UserIcon className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Complete Profile</h3>
              <p className="text-sm text-gray-600 mb-4">
                {mockUser.profileCompletion}% complete - Add more details
              </p>
              <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                Update Profile
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-white p-6 rounded-lg shadow-sm"
          >
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BellIcon className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Job Alerts</h3>
              <p className="text-sm text-gray-600 mb-4">
                Configure your notification preferences
              </p>
              <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                Set Alerts
              </button>
            </div>
          </motion.div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Job Matches */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="bg-white rounded-lg shadow-sm"
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Latest Job Matches
                  </h3>
                  <span className="text-sm text-blue-600 font-medium">
                    {mockStats.newMatchesToday} new today
                  </span>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {mockMatches.map((match) => (
                  <div key={match.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-1">
                          {match.title}
                        </h4>
                        <p className="text-gray-600">{match.company}</p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(match.matchScore)}`}>
                        {match.matchScore}% Match
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center">
                        <MapPinIcon className="w-4 h-4 mr-1" />
                        {match.location}
                      </div>
                      <div className="flex items-center">
                        <DollarSignIcon className="w-4 h-4 mr-1" />
                        {match.salary}
                      </div>
                      <div className="flex items-center">
                        <BriefcaseIcon className="w-4 h-4 mr-1" />
                        {match.workType}
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Matching Skills:</p>
                      <div className="flex flex-wrap gap-2">
                        {match.matchingSkills.map((skill, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">Posted {match.postedDate}</span>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                          View Details
                        </button>
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm">
                          Apply Now
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Applications */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="bg-white rounded-lg shadow-sm"
            >
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Recent Applications
                </h3>
              </div>
              
              <div className="p-6 space-y-4">
                {mockApplications.map((application) => (
                  <div key={application.id} className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {application.jobTitle}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">{application.company}</p>
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(application.status)}`}>
                        {application.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        {application.lastUpdate}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Profile Completion */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.9 }}
              className="bg-white rounded-lg shadow-sm"
            >
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Profile Completion
                </h3>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span>Profile Strength</span>
                    <span>{mockUser.profileCompletion}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${mockUser.profileCompletion}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      Resume uploaded
                    </span>
                    <span className="text-green-600">✓</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      Basic info complete
                    </span>
                    <span className="text-green-600">✓</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                      Add work preferences
                    </span>
                    <button className="text-blue-600 text-xs">Add</button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center">
                      <div className="w-2 h-2 bg-gray-300 rounded-full mr-2"></div>
                      Add portfolio links
                    </span>
                    <button className="text-blue-600 text-xs">Add</button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}