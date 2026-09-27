// Example Onboarding Flow with Fogg Behavior Model and Hook triggers
import React, { useState } from 'react';

export const OnboardingWizard = () => {
  const [step, setStep] = useState(1);
  const [projectTitle, setProjectTitle] = useState('');

  // 1-Click Fast-Path (Simplicity Lever: Minimal physical effort)
  const handleQuickCreate = () => {
    // Variable Reward: Instant Aha moment
    triggerConfetti();
    trackEvent('aha_moment_unlocked');
  };

  return (
    <div className="onboarding-container">
      {/* Endowed Progress: Step 2 of 3 (Head start momentum) */}
      <div className="progress-bar" data-step={step}>
        <span>Step 2 of 3: Setup your first workspace</span>
      </div>

      <input 
        name="workspaceName" 
        placeholder="Workspace name (e.g. Acme Studio)" 
        value={projectTitle}
        onChange={(e) => setProjectTitle(e.target.value)}
      />

      <button onClick={handleQuickCreate}>
        Start Creating (Instant Setup)
      </button>
    </div>
  );
};
