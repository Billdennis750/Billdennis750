import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '../ui/form';
import { Input } from '../ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Calculator, Clock, Calendar } from 'lucide-react';

const schema = z.object({
  loanAmount: z.string().min(1, 'Loan amount is required'),
  repaymentDuration: z.string().min(1, 'Please select repayment duration'),
  repaymentFrequency: z.string().min(1, 'Please select repayment frequency'),
});

const LoanPreferencesStep = ({ initialData, onNext, onBack }) => {
  const [repaymentEstimate, setRepaymentEstimate] = useState(null);

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      loanAmount: initialData.loanAmount || '',
      repaymentDuration: initialData.repaymentDuration || '',
      repaymentFrequency: initialData.repaymentFrequency || '',
    },
  });

  // Watch specific fields instead of entire form to prevent infinite loops
  const loanAmount = form.watch('loanAmount');
  const repaymentDuration = form.watch('repaymentDuration');
  const repaymentFrequency = form.watch('repaymentFrequency');

  useEffect(() => {
    if (loanAmount && repaymentDuration && repaymentFrequency) {
      const amount = parseFloat(loanAmount);
      if (amount > 0 && !isNaN(amount)) {
        calculateRepayment(amount, repaymentDuration, repaymentFrequency);
      }
    }
  }, [loanAmount, repaymentDuration, repaymentFrequency]);

  const calculateRepayment = (loanAmount, duration, frequency) => {
    // Interest rate: 5% per month
    const monthlyRate = 0.05;
    
    // Duration in months
    const durationMonths = {
      '3_months': 3,
      '6_months': 6,
      '9_months': 9,
      '12_months': 12
    }[duration] || 6;
    
    // Total interest
    const totalInterest = loanAmount * monthlyRate * durationMonths;
    const totalAmount = loanAmount + totalInterest;
    
    // Payments per month based on frequency
    const paymentsPerMonth = {
      'weekly': 4,
      'bi_weekly': 2,
      'monthly': 1
    }[frequency] || 1;
    
    const totalPayments = durationMonths * paymentsPerMonth;
    const paymentAmount = totalAmount / totalPayments;
    
    setRepaymentEstimate({
      loanAmount,
      totalInterest: Math.round(totalInterest),
      totalAmount: Math.round(totalAmount),
      durationMonths,
      frequency,
      totalPayments,
      paymentAmount: Math.round(paymentAmount),
      monthlyRate: monthlyRate * 100
    });
  };

  const getFrequencyLabel = (frequency) => {
    return {
      'weekly': 'week',
      'bi_weekly': '2 weeks',
      'monthly': 'month'
    }[frequency] || 'payment';
  };

  const onSubmit = (data) => {
    onNext({
      ...data,
      repaymentEstimate
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="loanAmount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Loan Amount Requested (₦) *</FormLabel>
              <FormControl>
                <Input 
                  type="number" 
                  placeholder="2000000" 
                  min="100000"
                  max="15000000"
                  {...field} 
                />
              </FormControl>
              <FormDescription>
                Enter amount between ₦100,000 and ₦15,000,000
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="repaymentDuration"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Repayment Duration *
              </FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select duration" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="3_months">3 Months</SelectItem>
                  <SelectItem value="6_months">6 Months</SelectItem>
                  <SelectItem value="9_months">9 Months</SelectItem>
                  <SelectItem value="12_months">12 Months</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="repaymentFrequency"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Repayment Frequency *
              </FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="bi_weekly">Bi-Weekly (Every 2 Weeks)</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Repayment Estimate Card */}
        {repaymentEstimate && (
          <div className="p-6 rounded-lg border-2" style={{ borderColor: 'var(--accent-text)', background: 'var(--accent-wash)' }}>
            <div className="flex items-center gap-2 mb-4">
              <Calculator className="w-5 h-5" style={{ color: 'var(--accent-text)' }} />
              <h3 className="font-semibold" style={{ color: 'var(--accent-text)' }}>Estimated Repayment</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="body-small" style={{ color: 'var(--text-muted)' }}>Loan Amount</p>
                <p className="font-semibold">₦{repaymentEstimate.loanAmount.toLocaleString()}</p>
              </div>
              <div>
                <p className="body-small" style={{ color: 'var(--text-muted)' }}>Interest ({repaymentEstimate.monthlyRate}%/month)</p>
                <p className="font-semibold">₦{repaymentEstimate.totalInterest.toLocaleString()}</p>
              </div>
              <div>
                <p className="body-small" style={{ color: 'var(--text-muted)' }}>Total Repayment</p>
                <p className="font-semibold">₦{repaymentEstimate.totalAmount.toLocaleString()}</p>
              </div>
              <div>
                <p className="body-small" style={{ color: 'var(--text-muted)' }}>Number of Payments</p>
                <p className="font-semibold">{repaymentEstimate.totalPayments} payments</p>
              </div>
            </div>
            
            <div className="p-4 rounded-lg bg-white">
              <p className="body-small" style={{ color: 'var(--text-muted)' }}>Amount per {getFrequencyLabel(repaymentEstimate.frequency)}</p>
              <p className="text-2xl font-bold" style={{ color: 'var(--accent-text)' }}>
                ₦{repaymentEstimate.paymentAmount.toLocaleString()}
              </p>
            </div>
          </div>
        )}

        <div className="p-4 rounded-lg" style={{ background: 'var(--bg-section)' }}>
          <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
            <strong>Note:</strong> The repayment schedule will begin after your loan is disbursed. 
            You will receive email reminders before each payment due date. 
            Early repayment is allowed without penalties.
          </p>
        </div>

        <div className="flex justify-between">
          <Button type="button" onClick={onBack} variant="outline" className="rounded-full">
            Back
          </Button>
          <Button type="submit" className="btn-primary">
            Next Step
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default LoanPreferencesStep;
