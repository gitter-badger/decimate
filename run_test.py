#!/sw/xc40/python/2.7.11/sles11.3_gnu5.1.0/bin/python
# 
# --- decimate (version 0.4) --
# Samuel KORTAS, KAUST Supercomputing Laboraory

# samuel.kortas@kaust.edu.sa

# Supercomputing Laboratory
# Core Labs Division
# King Abdullah University of Science and Technology
# Copyright (c) 2017, 
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.

from decimate import *
import datetime,time

  
import glob
import traceback
import pprint

class decimate_test(decimate):

  def __init__(self):

    decimate.__init__(self,app_name='decimatest', decimate_version_required='0.3',app_version='0.1')


    

  #########################################################################


  def user_initialize_parser(self):
    self.parser.add_argument("-b", "--begins", type=int, help='run simulation up to this step',default=1)
    self.parser.add_argument("-e", "--ends", type=int, help='run simulation up to this step',default=10)
    self.parser.add_argument("-a", "--array", type=str, help='size of the array submitted at each step',default='1-3')
    self.parser.add_argument("-n", "--ntasks", type=int, help='number of tasks for the jobs',default=1)
    self.parser.add_argument("-t", "--time", type=str, help='ellapse time',default='00:05:00')

  #########################################################################
  # create job files
  #########################################################################
  
  def create_job_files(self):


      self.log_debug('from step=%s to %s ' % (self.args.begins,self.args.ends))

      for step in range(self.args.begins,self.args.ends+1):

        self.log_info('creating job files for step %d' % step)

        output = """\
######################
# Begin work section #
######################

# Print this sub-job's task ID
echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

#sleep 10
"""
        
        
        input_file = '%s/templates/filter_first.job.template' 
        open("%s/%d.job" % (self.SAVE_DIR,step), "w").write(output)


      # finish job
      open("%s/%d-finish.job" % (self.SAVE_DIR,step), "w").write(output)

  
  #########################################################################
  # submitting all the first jobs
  #########################################################################

  def user_launch_jobs(self,reading_input = True):


    #self.log_info('ZZZZZZZZZZZZZ setting max_retry to 1 ZZZZZZZZZZZZ')
    self.load()

    # cleaning SAVE directory
    self.system('rm %s/Done*'% self.SAVE_DIR)
    self.system('rm %s/Complete*'% self.SAVE_DIR)
    self.system('rm %s/*job*'% self.SAVE_DIR)

      
    self.create_job_files()

    self.ask("Ready... All set... Go? ", default='y' )

    dep = step_before = job_before = last_task_id_before =  None
                     
    for step in range(self.args.begins,self.args.ends+1):

        last_task_id = 1
        array_item = None
        
        job_name = '%s'  % (step)
        job_script = '%s/%s.job' % (self.SAVE_DIR,job_name)
        
        array_item = "%s" % self.args.array

        new_job = { 'name' : job_name,
                    'comes_before': None,
                    'comes_after': dep,
                    'make_depend' : None,
                    'dependency' : dep,
                    'step_before' : step_before,
                    'script' : os.path.abspath("%s" % job_script),
                    'ntasks' : self.args.ntasks,
                    'time'   : self.args.time,
                    'account' : 'k01',
                    'output_name' : '%s.out' % step,
                    'error_name' :  '%s.err' % step,
                    'submit_dir' : os.getcwd(),
                    'array' : array_item,
                    'last_task_id' : last_task_id,
                    'last_task_id_before' : last_task_id_before,
                    'attempt' : 0
        }

        new_job_script_content = self.wrap_job_script(new_job)

        f = open("%s+" % job_script,'w')
        f.write(new_job_script_content)
        f.close()

        new_job['script_file'] = job_script+'+'


        (job_id, cmd) = self.submit_job(new_job)
        
        dep = job_id
        step_before = job_name
        last_task_id_before = last_task_id




  #########################################################################
  # checking job correct completion
  #########################################################################

  def fake_job(self,step,task,attempt):

    self.log_info('faking step %s task %s attempt %s' % (step,task,attempt))


  #########################################################################
  # checking job correct completion
  #########################################################################

  def check_job(self,what,task_id,running_dir,output_file,error_file,is_job_completed):

    return is_job_completed
    
if __name__ == "__main__":
    K=decimate_test()
    K.start()