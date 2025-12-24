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
import { Textarea } from '../ui/textarea';

// Phone validation: exactly 11 digits, numbers only
const phoneRegex = /^[0-9]{11}$/;

const schema = z.object({
  fullName: z.string().min(2, 'Full name must be at least 2 characters'),
  dateOfBirth: z.string().min(1, 'Date of birth is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string()
    .regex(phoneRegex, 'Phone number must be exactly 11 digits (numbers only)'),
  secondaryPhone: z.string()
    .regex(phoneRegex, 'Secondary phone must be exactly 11 digits (numbers only)')
    .optional()
    .or(z.literal('')),
  relativePhone: z.string()
    .regex(phoneRegex, "Relative's phone must be exactly 11 digits (numbers only)"),
  homeTown: z.string().min(2, 'Home town is required'),
  flatHouseNumber: z.string().min(1, 'Flat/House number is required'),
  residentialAddress: z.string().min(10, 'Residential address is required'),
});

const PersonalInfoStep = ({ initialData, onNext }) => {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      fullName: initialData.fullName || '',
      dateOfBirth: initialData.dateOfBirth || '',
      email: initialData.email || '',
      phone: initialData.phone || '',
      secondaryPhone: initialData.secondaryPhone || '',
      relativePhone: initialData.relativePhone || '',
      homeTown: initialData.homeTown || '',
      flatHouseNumber: initialData.flatHouseNumber || '',
      residentialAddress: initialData.residentialAddress || '',
    },
  });

  // Handle phone input to only allow numbers
  const handlePhoneInput = (e, field) => {
    const value = e.target.value.replace(/[^0-9]/g, '').slice(0, 11);
    field.onChange(value);
  };

  const onSubmit = (data) => {
    onNext(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="fullName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full Name *</FormLabel>
              <FormControl>
                <Input placeholder="John Doe" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="dateOfBirth"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Date of Birth *</FormLabel>
              <FormControl>
                <Input type="date" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email Address *</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john.doe@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone Number *</FormLabel>
              <FormControl>
                <Input 
                  placeholder="08012345678" 
                  maxLength={11}
                  value={field.value}
                  onChange={(e) => handlePhoneInput(e, field)}
                />
              </FormControl>
              <FormDescription>Enter 11 digits, numbers only</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="secondaryPhone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Secondary Phone Number</FormLabel>
              <FormControl>
                <Input 
                  placeholder="08098765432" 
                  maxLength={11}
                  value={field.value}
                  onChange={(e) => handlePhoneInput(e, field)}
                />
              </FormControl>
              <FormDescription>Optional - Enter 11 digits, numbers only</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="relativePhone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Relative's Phone Number *</FormLabel>
              <FormControl>
                <Input 
                  placeholder="08011223344" 
                  maxLength={11}
                  value={field.value}
                  onChange={(e) => handlePhoneInput(e, field)}
                />
              </FormControl>
              <FormDescription>Enter 11 digits, numbers only (for emergency contact)</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="homeTown"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Home Town *</FormLabel>
              <FormControl>
                <Input placeholder="Lagos" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="flatHouseNumber"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Flat / House Number *</FormLabel>
              <FormControl>
                <Input placeholder="e.g., 12A, Flat 5, Block B" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="residentialAddress"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Residential Address *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="123 Main Street, Victoria Island, Lagos"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end">
          <Button type="submit" className="btn-primary">
            Next Step
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default PersonalInfoStep;
