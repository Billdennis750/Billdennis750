import React from 'react';
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
import { Building2 } from 'lucide-react';

const nigerianBanks = [
  "Access Bank",
  "Citibank Nigeria",
  "Ecobank Nigeria",
  "Fidelity Bank",
  "First Bank of Nigeria",
  "First City Monument Bank (FCMB)",
  "Globus Bank",
  "Guaranty Trust Bank (GTBank)",
  "Heritage Bank",
  "Jaiz Bank",
  "Keystone Bank",
  "Kuda Bank",
  "Opay",
  "Palmpay",
  "Parallex Bank",
  "Polaris Bank",
  "Providus Bank",
  "Stanbic IBTC Bank",
  "Standard Chartered Bank",
  "Sterling Bank",
  "SunTrust Bank",
  "Titan Trust Bank",
  "Union Bank of Nigeria",
  "United Bank for Africa (UBA)",
  "Unity Bank",
  "VFD Microfinance Bank",
  "Wema Bank",
  "Zenith Bank"
];

const schema = z.object({
  bankName: z.string().min(1, 'Please select your bank'),
  accountName: z.string().min(2, 'Account name is required'),
  accountNumber: z.string().length(10, 'Account number must be 10 digits'),
});

const BankDetailsStep = ({ initialData, onNext, onBack }) => {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      bankName: initialData.bankName || '',
      accountName: initialData.accountName || '',
      accountNumber: initialData.accountNumber || '',
    },
  });

  const onSubmit = (data) => {
    onNext(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="flex items-center gap-3 mb-6 p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
          <Building2 className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
          <div>
            <p className="font-medium" style={{ color: 'var(--text-primary)' }}>Bank Account for Loan Credit</p>
            <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
              Your approved loan will be credited to this account only.
            </p>
          </div>
        </div>

        <FormField
          control={form.control}
          name="bankName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bank Name *</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your bank" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {nigerianBanks.map((bank) => (
                    <SelectItem key={bank} value={bank}>{bank}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="accountName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Account Name *</FormLabel>
              <FormControl>
                <Input placeholder="John Doe" {...field} />
              </FormControl>
              <FormDescription>
                Enter the name as it appears on your bank account
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="accountNumber"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Account Number *</FormLabel>
              <FormControl>
                <Input 
                  placeholder="0123456789" 
                  maxLength={10}
                  {...field} 
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    field.onChange(value);
                  }}
                />
              </FormControl>
              <FormDescription>
                Enter your 10-digit account number
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="p-4 rounded-lg border border-yellow-300 bg-yellow-50">
          <p className="body-small text-yellow-800">
            <strong>Important:</strong> Please ensure your bank details are correct. 
            Loan funds will be credited only to this account and cannot be changed after submission.
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

export default BankDetailsStep;
