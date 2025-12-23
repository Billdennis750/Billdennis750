import React, { useState } from 'react';
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
import { Upload, Lock, Eye, EyeOff } from 'lucide-react';

const schema = z.object({
  nin: z.string().min(11, 'NIN must be at least 11 characters'),
  bvn: z.string().min(11, 'BVN must be at least 11 characters'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

const IdentityStep = ({ initialData, onNext, onBack }) => {
  const [idCard, setIdCard] = useState(null);
  const [passport, setPassport] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      nin: initialData.nin || '',
      bvn: initialData.bvn || '',
      password: '',
      confirmPassword: '',
    },
  });

  const handleFileChange = (e, type) => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'idCard') {
        setIdCard(file);
      } else {
        setPassport(file);
      }
    }
  };

  const onSubmit = (data) => {
    if (!idCard) {
      alert('Please upload your ID card');
      return;
    }
    if (!passport) {
      alert('Please upload your passport photograph');
      return;
    }
    
    onNext({
      nin: data.nin,
      bvn: data.bvn,
      password: data.password,
      idCard: idCard,
      passport: passport,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Identity Verification Section */}
        <div className="space-y-6">
          <h3 className="font-semibold text-lg">Identity Verification</h3>
          
          <FormField
            control={form.control}
            name="nin"
            render={({ field }) => (
              <FormItem>
                <FormLabel>National Identification Number (NIN) *</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="12345678901" 
                    maxLength={11}
                    {...field} 
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '');
                      field.onChange(value);
                    }}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="bvn"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Bank Verification Number (BVN) *</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="12345678901" 
                    maxLength={11}
                    {...field}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '');
                      field.onChange(value);
                    }}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* ID Card Upload */}
          <div className="space-y-2">
            <FormLabel>Upload Valid Government-Issued ID Card *</FormLabel>
            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-green-500 transition-colors ${idCard ? 'border-green-500 bg-green-50' : ''}`}
              onClick={() => document.getElementById('idCard').click()}
            >
              <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: idCard ? 'var(--accent-text)' : 'var(--text-muted)' }} />
              <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                {idCard ? `✓ ${idCard.name}` : "Click to upload ID card (Driver's License, Voter's Card, NIN Slip, etc.)"}
              </p>
              <input
                id="idCard"
                type="file"
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => handleFileChange(e, 'idCard')}
              />
            </div>
          </div>

          {/* Passport Upload */}
          <div className="space-y-2">
            <FormLabel>Upload Passport Photograph *</FormLabel>
            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-green-500 transition-colors ${passport ? 'border-green-500 bg-green-50' : ''}`}
              onClick={() => document.getElementById('passport').click()}
            >
              <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: passport ? 'var(--accent-text)' : 'var(--text-muted)' }} />
              <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                {passport ? `✓ ${passport.name}` : 'Click to upload passport photograph'}
              </p>
              <input
                id="passport"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFileChange(e, 'passport')}
              />
            </div>
          </div>
        </div>

        {/* Account Creation Section */}
        <div className="pt-6 border-t space-y-6">
          <div className="flex items-center gap-3 mb-4 p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
            <Lock className="w-6 h-6" style={{ color: 'var(--accent-text)' }} />
            <div>
              <p className="font-medium" style={{ color: 'var(--text-primary)' }}>Create Your Account</p>
              <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
                Set a password to access your dashboard and track your application.
              </p>
            </div>
          </div>

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Create Password *</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input 
                      type={showPassword ? "text" : "password"} 
                      placeholder="••••••••" 
                      {...field} 
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 -translate-y-1/2"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </FormControl>
                <FormDescription>
                  Minimum 6 characters. You'll use this to login to your dashboard.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirm Password *</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input 
                      type={showConfirmPassword ? "text" : "password"} 
                      placeholder="••••••••" 
                      {...field} 
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 -translate-y-1/2"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
          <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
            <strong>Important:</strong> All uploaded documents must be clear and legible.
            Ensure your ID card is valid and not expired. Your information will be
            verified against NIMC and banking records. Your password is encrypted and secure.
          </p>
        </div>

        <div className="flex justify-between">
          <Button type="button" onClick={onBack} variant="outline" className="rounded-full">
            Back
          </Button>
          <Button type="submit" className="btn-primary">
            Submit Application
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default IdentityStep;
