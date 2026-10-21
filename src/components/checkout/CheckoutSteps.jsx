import React from 'react';
import { Check } from 'lucide-react';

export const CheckoutSteps = ({ currentStep = 1 }) => {
  const steps = [
    { number: 1, label: 'Cart' },
    { number: 2, label: 'Delivery Address' },
    { number: 3, label: 'Order Summary' },
    { number: 4, label: 'Payment' },
  ];

  return (
    <div className="w-full py-4 mb-8">
      <div className="flex items-center justify-between max-w-2xl mx-auto">
        {steps.map((step, idx) => {
          const isDone = step.number < currentStep;
          const isCurrent = step.number === currentStep;

          return (
            <React.Fragment key={step.number}>
              <div className="flex flex-col items-center gap-1.5 z-10">
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center font-extrabold text-xs transition-all ${
                    isDone
                      ? 'bg-emerald-600 text-white shadow-md'
                      : isCurrent
                      ? 'bg-indigo-600 text-white ring-4 ring-indigo-100 shadow-md'
                      : 'bg-gray-100 text-gray-400 border border-gray-200'
                  }`}
                >
                  {isDone ? <Check className="w-4 h-4" /> : step.number}
                </div>
                <span
                  className={`text-xs font-bold ${
                    isCurrent ? 'text-indigo-600' : isDone ? 'text-gray-800' : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>
              </div>

              {idx < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 -mt-5 transition-all ${
                    step.number < currentStep ? 'bg-emerald-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default CheckoutSteps;
