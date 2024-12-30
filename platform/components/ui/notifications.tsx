'use client'

import React from 'react';
import { useNotification } from '@/context/NotificationContext';
import { motion, AnimatePresence } from 'framer-motion';

const notificationStyles: Record<string, string> = {
  info: 'bg-white border-primary text-primary',
  success: 'bg-white border-green-500 text-green-700',
  error: 'bg-white border-red-500 text-red-700',
  warning: 'bg-white border-yellow-500 text-yellow-700',
};

const Notifications: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col space-y-2">
      <div className="w-[400px]">
        <AnimatePresence>
          {notifications.map((notification) => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`border-l-4 p-4 rounded shadow ${notificationStyles[notification.type]} w-full mb-2`}
            >
              <div className="flex justify-between items-start">
                <div className="flex flex-col gap-1 min-w-0 flex-1">
                  <div className="break-words">
                    {notification.message}
                  </div>
                  {notification.action && (
                    <span
                      onClick={() => {
                        notification.action?.onClick();
                        removeNotification(notification.id);
                      }}
                      className="text-sm underline cursor-pointer"
                      style={{ color: 'inherit' }}
                    >
                      {notification.action.label}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => removeNotification(notification.id)}
                  className="ml-4 text-lg leading-none focus:outline-none shrink-0"
                >
                  &times;
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Notifications;
