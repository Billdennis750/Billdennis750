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
import { Upload } from 'lucide-react';

const schema = z.object({
  nin: z.string().min(11, 'NIN must be at least 11 characters'),
  bvn: z.string().min(11, 'BVN must be at least 11 characters'),
});

const IdentityStep = ({ initialData, onNext, onBack }) => {
  const [idCard, setIdCard] = useState(null);
  const [passport, setPassport] = useState(null);
  
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      nin: initialData.nin || '',
      bvn: initialData.bvn || '',
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
    onNext({
      ...data,
      idCard: idCard,
      passport: passport,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="nin"
          render={({ field }) => (
            <FormItem>
              <FormLabel>National Identification Number (NIN) *</FormLabel>
              <FormControl>
                <Input placeholder="12345678901" {...field} />
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
                <Input placeholder="12345678901" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* ID Card Upload */}
        <div className="space-y-2">
          <FormLabel>Upload Valid Government-Issued ID Card *</FormLabel>
          <div
            className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-green-500 transition-colors"
            onClick={() => document.getElementById('idCard').click()}
          >
            <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--text-muted)' }} />
            <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
              {idCard ? idCard.name : 'Click to upload ID card (Driver\'s License, Voter\'s Card, etc.)'}
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
            className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-green-500 transition-colors"
            onClick={() => document.getElementById('passport').click()}
          >
            <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--text-muted)' }} />
            <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
              {passport ? passport.name : 'Click to upload passport photograph'}
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

        <div className="p-4 rounded-lg" style={{ background: 'var(--accent-wash)' }}>
          <p className="body-small" style={{ color: 'var(--text-secondary)' }}>
            <strong>Important:</strong> All uploaded documents must be clear and legible.
            Ensure your ID card is valid and not expired. Your information will be
            verified against NIMC and banking records.
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
