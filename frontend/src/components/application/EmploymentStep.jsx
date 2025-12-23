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
} from '../ui/form';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

const schema = z.object({
  placeOfWork: z.string().min(2, 'Place of work is required'),
  employmentStatus: z.string().min(1, 'Employment status is required'),
  employmentDetails: z.string().min(10, 'Employment details are required'),
  monthlyIncome: z.string().min(1, 'Monthly income is required'),
  loanReason: z.string().min(10, 'Please provide reason for loan'),
  loanAmount: z.string().min(1, 'Loan amount is required'),
});

const EmploymentStep = ({ initialData, onNext, onBack }) => {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      placeOfWork: initialData.placeOfWork || '',
      employmentStatus: initialData.employmentStatus || '',
      employmentDetails: initialData.employmentDetails || '',
      monthlyIncome: initialData.monthlyIncome || '',
      loanReason: initialData.loanReason || '',
      loanAmount: initialData.loanAmount || '',
    },
  });

  const onSubmit = (data) => {
    onNext(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="placeOfWork"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Place of Work *</FormLabel>
              <FormControl>
                <Input placeholder="Company Name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="employmentStatus"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Employment Status *</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select employment status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="employed">Employed</SelectItem>
                  <SelectItem value="self-employed">Self-Employed</SelectItem>
                  <SelectItem value="business-owner">Business Owner</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="employmentDetails"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Employment Details *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe your employment, job role, or business"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="monthlyIncome"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Monthly Income (₦) *</FormLabel>
              <FormControl>
                <Input type="number" placeholder="250000" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="loanAmount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Loan Amount (₦) *</FormLabel>
              <FormControl>
                <Input type="number" placeholder="1000000" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="loanReason"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Reason for Loan *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Explain why you need this loan and how you plan to use it"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

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

export default EmploymentStep;
